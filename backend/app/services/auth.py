from sqlalchemy.orm import Session

from app.core import security
from app.models import User


class AuthError(Exception):
    pass


def register_user(db: Session, email: str, password: str, full_name: str | None) -> User:
    if db.query(User).filter(User.email == email).first():
        raise AuthError("email already registered")
    user = User(email=email, password_hash=security.hash_password(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not security.verify_password(password, user.password_hash):
        raise AuthError("invalid credentials")
    return user
