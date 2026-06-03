"""
Конфигурация из .env файла
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    OWM_API_KEY: str  # OpenWeatherMap API key

    # Лимит бесплатных запросов в день
    FREE_DAILY_LIMIT: int = 5

    # Стоимость подписки в Stars
    PREMIUM_PRICE_STARS: int = 99

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
