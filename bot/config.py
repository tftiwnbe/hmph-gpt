from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    # Main
    LOG_LEVEL: str = "INFO"
    DEVELOPMENT: bool = False
    IN_CONTAINER: bool = False
    SUPERUSER_TG_ID: int = 00

    # Tokens
    BOT_TOKEN: SecretStr = SecretStr("")
    OPENAI_TOKEN: SecretStr = SecretStr("")

    # PostgreSQL
    ECHO_SQL: bool = False
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""


settings = Settings()
