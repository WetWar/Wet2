from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    OWM_API_KEY: str

    FREE_DAILY_LIMIT: int = 5      # 5 бесплатных запросов в день
    PREMIUM_PRICE_STARS: int = 49  # 49 Stars

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
