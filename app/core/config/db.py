from .base import BaseConfig

class DBConfig(BaseConfig):
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "learning_assistant"
    DATABASE_URL: str | None = None

    @property
    def url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'