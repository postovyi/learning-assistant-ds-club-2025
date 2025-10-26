from .ai import AIConfig
from .db import DBConfig

class Settings:
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = "DEBUG"

    ai = AIConfig()
    db = DBConfig()

settings = Settings()