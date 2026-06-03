"""
Асинхронный планировщик утренней рассылки.

Каждый день в 8:00 МСК отправляет прогноз на день всем пользователям,
у которых сохранён город.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Bot

import storage
import weather as w

logger = logging.getLogger(__name__)

MSK = timezone(timedelta(hours=3))
SEND_HOUR   = 8  # 8:00 МСК
SEND_MINUTE = 0


def _seconds_until_next_send() -> float:
    """Считает, сколько секунд до следующего 8:00 МСК."""
    now = datetime.now(MSK)
    target = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
    if now >= target:
        # Уже прошло — ждём до завтра
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def send_morning_digest(bot: Bot):
    """Рассылает утренний прогноз всем пользователям."""
    users = storage.get_all_users_with_cities()
    logger.info("Утренняя рассылка: %d пользователей", len(users))

    for user_id_str, city in users.items():
        user_id = int(user_id_str)
        try:
            forecast = await w.get_forecast(city)
            if not forecast:
                logger.warning("Нет прогноза для %s (user %s)", city, user_id)
                continue

            text = w.format_morning_digest(city, forecast)
            await bot.send_message(user_id, text, parse_mode="HTML")

        except Exception as e:
            # Пользователь мог заблокировать бота — не падаем
            logger.warning("Не удалось отправить рассылку user %s: %s", user_id, e)

        # Небольшая пауза, чтобы не словить rate limit Telegram
        await asyncio.sleep(0.05)


async def start_scheduler(bot: Bot):
    """Бесконечный цикл: ждём 8:00 МСК → рассылаем → ждём снова."""
    logger.info("Планировщик запущен")
    while True:
        wait = _seconds_until_next_send()
        next_run = datetime.now(MSK) + timedelta(seconds=wait)
        logger.info(
            "Следующая рассылка в %s МСК (через %.0f сек)",
            next_run.strftime("%Y-%m-%d %H:%M"),
            wait,
        )
        await asyncio.sleep(wait)
        await send_morning_digest(bot)
