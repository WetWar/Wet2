"""
Погодный Telegram-бот на aiogram 3.x
Запуск: python bot.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import router
from scheduler import start_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутер с хэндлерами
    dp.include_router(router)

    # Запускаем планировщик утренней рассылки
    asyncio.create_task(start_scheduler(bot))

    logger.info("Бот запущен")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
