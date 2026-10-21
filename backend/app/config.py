from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "NEXUSTRACE AI"
    DATABASE_URL: str = "sqlite:///./nexustrace.db"
    SECRET_KEY: str = "change-me-before-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173"
    AI_PROVIDER: str = "none"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
