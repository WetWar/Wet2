"""
Асинхронный планировщик утренней рассылки (8:00 МСК).
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Bot

import storage
import weather as w

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))
SEND_HOUR   = 8
SEND_MINUTE = 0


def _seconds_until_next_send() -> float:
    now    = datetime.now(MSK)
    target = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def send_morning_digest(bot: Bot):
    users = storage.get_all_users_with_cities()
    logger.info("Утренняя рассылка: %d пользователей", len(users))

    for user_id_str, city in users.items():
        user_id = int(user_id_str)
        lang    = storage.get_lang(user_id) or "ru"
        try:
            forecast = await w.get_forecast(city, lang)
            if not forecast:
                continue
            text = w.format_morning_digest(city, forecast, lang)
            await bot.send_message(user_id, text, parse_mode="HTML")
        except Exception as e:
            logger.warning("Не удалось отправить user %s: %s", user_id, e)
        await asyncio.sleep(0.05)


async def start_scheduler(bot: Bot):
    logger.info("Планировщик запущен")
    while True:
        wait     = _seconds_until_next_send()
        next_run = datetime.now(MSK) + timedelta(seconds=wait)
        logger.info("Следующая рассылка в %s МСК (через %.0f сек)",
                    next_run.strftime("%Y-%m-%d %H:%M"), wait)
        await asyncio.sleep(wait)
        await send_morning_digest(bot)
