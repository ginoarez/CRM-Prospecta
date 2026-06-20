from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://prospecta:prospecta@localhost:5432/prospecta"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_EMAIL: str = "admin@agencia.com"
    ADMIN_PASSWORD: str = "change-me"
    CORS_ORIGINS: str = "http://localhost:3000"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    GEO_HTTP_TIMEOUT: float = 30.0
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-opus-4-8"
    ANTHROPIC_API_KEY: str = ""
    SCRAPE_TIMEOUT: float = 10.0
    AGENCY_NAME: str = "Tu Agencia"
    AGENCY_TAGLINE: str = "IA, automatización y crecimiento"
    AGENCY_EMAIL: str = "hola@tuagencia.com"
    AGENCY_PHONE: str = "+57 300 000 0000"
    AGENCY_LOGO_URL: str = ""
    AGENCY_COLOR: str = "#2563eb"
    PROPOSALS_DIR: str = "storage/proposals"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "hola@tuagencia.com"
    SMTP_FROM_NAME: str = "Tu Agencia"
    SMTP_STARTTLS: bool = True
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_BUSINESS_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_API_URL: str = "https://graph.facebook.com"
    WHATSAPP_API_VERSION: str = "v21.0"


settings = Settings()
