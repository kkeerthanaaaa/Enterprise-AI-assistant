from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://ai_user:ai_password@localhost:5432/enterprise_ai"

    # Auth
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM
    LLM_PROVIDER: str = "openai"  # openai | local
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-5"
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434/v1"

    # Embeddings
    EMBEDDING_PROVIDER: str = "local"  # local | openai
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    # Storage
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_MB: int = 25

    # App
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
