from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User
from app.core import security


def main():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
            print("admin already exists")
            return
        db.add(User(
            email=settings.ADMIN_EMAIL,
            password_hash=security.hash_password(settings.ADMIN_PASSWORD),
            full_name="Admin",
            role="admin",
        ))
        db.commit()
        print(f"created admin {settings.ADMIN_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
