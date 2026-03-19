from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    VALKEY_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 4
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    SENTRY_DSN: str = ""
    PRINT_AGENT_KEY: str = ""     # shared secret for print agent auth


settings = Settings()
