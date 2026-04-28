from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./jewelry.db"
    JWT_SECRET: str = "longshi-dev-secret-change-in-prod"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()


class BizError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
