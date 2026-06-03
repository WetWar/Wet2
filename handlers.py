"""
Хэндлеры бота: /start, /now, /hourly, /subscribe, оплата Stars.
"""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import settings
import storage
import weather as w

logger = logging.getLogger(__name__)
router = Router()


# ─────────────────────────── FSM ────────────────────────────────────────

class CitySetup(StatesGroup):
    waiting_for_city = State()


# ─────────────────────────── лимиты ─────────────────────────────────────

async def check_limit(message: Message) -> bool:
    """
    Возвращает True, если запрос разрешён.
    Списывает один запрос из лимита (если не premium).
    """
    uid = message.from_user.id

    if storage.is_premium(uid):
        return True  # premium — без ограничений

    used = storage.get_requests_today(uid)
    if used >= settings.FREE_DAILY_LIMIT:
        await message.answer(
            f"🚫 Вы использовали все <b>{settings.FREE_DAILY_LIMIT}</b> бесплатных запроса сегодня.\n\n"
            f"💎 Оформите подписку за <b>{settings.PREMIUM_PRICE_STARS} Stars</b> "
            f"и получите безлимитный доступ.\n\n"
            f"👇 Нажмите /subscribe для оплаты.",
            parse_mode="HTML",
        )
        return False

    storage.increment_requests(uid)
    remaining = settings.FREE_DAILY_LIMIT - used - 1
    if remaining <= 1:
        await message.answer(
            f"⚠️ Осталось <b>{remaining}</b> бесплатных запросов на сегодня.\n"
            f"Подписка — /subscribe",
            parse_mode="HTML",
        )
    return True


# ─────────────────────────── /start ─────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    city = storage.get_city(uid)

    if city:
        await message.answer(
            f"👋 С возвращением! Ваш город: <b>{city}</b>.\n\n"
            f"Команды:\n"
            f"/now — погода прямо сейчас\n"
            f"/hourly — прогноз на ближайшие часы\n"
            f"/city — сменить город\n"
            f"/subscribe — Premium подписка\n",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "👋 Привет! Я погодный бот.\n\n"
            "🏙 Введите название вашего города (на русском или английском):",
        )
        await state.set_state(CitySetup.waiting_for_city)


@router.message(Command("city"))
async def cmd_change_city(message: Message, state: FSMContext):
    await message.answer("🏙 Введите новое название города:")
    await state.set_state(CitySetup.waiting_for_city)


# ─────────────────────────── обработка города ───────────────────────────

@router.message(CitySetup.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city_input = message.text.strip()
    await message.answer("🔍 Проверяю город...")

    validated = await w.validate_city(city_input)

    if not validated:
        await message.answer(
            f"❌ Город <b>{city_input}</b> не найден.\n"
            "Попробуйте ещё раз (проверьте написание):",
            parse_mode="HTML",
        )
        return  # остаёмся в том же состоянии

    storage.set_city(message.from_user.id, validated)
    await state.clear()

    await message.answer(
        f"✅ Город <b>{validated}</b> сохранён!\n\n"
        f"Команды:\n"
        f"/now — погода сейчас\n"
        f"/hourly — прогноз на ближайшие часы\n"
        f"/subscribe — Premium подписка\n\n"
        f"Каждое утро в 8:00 МСК я буду присылать прогноз на день 🌅",
        parse_mode="HTML",
    )


# ─────────────────────────── /now ───────────────────────────────────────

@router.message(Command("now"))
async def cmd_now(message: Message):
    uid  = message.from_user.id
    city = storage.get_city(uid)

    if not city:
        await message.answer("Сначала укажите город командой /start")
        return

    if not await check_limit(message):
        return

    data = await w.get_current_weather(city)
    if not data:
        await message.answer("⚠️ Не удалось получить данные. Попробуйте позже.")
        return

    await message.answer(w.format_current(data), parse_mode="HTML")


# ─────────────────────────── /hourly ────────────────────────────────────

@router.message(Command("hourly"))
async def cmd_hourly(message: Message):
    uid  = message.from_user.id
    city = storage.get_city(uid)

    if not city:
        await message.answer("Сначала укажите город командой /start")
        return

    if not await check_limit(message):
        return

    forecast = await w.get_forecast(city)
    if not forecast:
        await message.answer("⚠️ Не удалось получить прогноз. Попробуйте позже.")
        return

    await message.answer(w.format_hourly(forecast), parse_mode="HTML")


# ─────────────────────────── /subscribe (Stars) ─────────────────────────

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    uid = message.from_user.id

    if storage.is_premium(uid):
        await message.answer("✅ У вас уже активна Premium подписка!")
        return

    used = storage.get_requests_today(uid)
    await message.answer(
        f"💎 <b>Premium подписка</b>\n\n"
        f"Использовано сегодня: {used}/{settings.FREE_DAILY_LIMIT}\n\n"
        f"Что входит:\n"
        f"• Безлимитные запросы /now и /hourly\n"
        f"• Утренний прогноз каждый день\n\n"
        f"Стоимость: <b>{settings.PREMIUM_PRICE_STARS} ⭐ Telegram Stars</b>\n\n"
        f"👇 Нажмите кнопку для оплаты:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=f"⭐ Оплатить {settings.PREMIUM_PRICE_STARS} Stars",
                    callback_data="pay_stars",
                )
            ]]
        ),
    )


@router.callback_query(F.data == "pay_stars")
async def process_pay_callback(callback):
    await callback.answer()
    await callback.message.answer_invoice(
        title="🌤 WeatherBot Premium",
        description="Безлимитный доступ к прогнозам погоды",
        payload="premium_subscription",
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="Premium", amount=settings.PREMIUM_PRICE_STARS)],
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    """Обязательное подтверждение перед списанием Stars."""
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    """Обработка успешной оплаты."""
    uid = message.from_user.id
    storage.set_premium(uid)

    logger.info(
        "Пользователь %s оплатил Premium. "
        "payment_id=%s",
        uid,
        message.successful_payment.telegram_payment_charge_id,
    )

    await message.answer(
        "🎉 Оплата прошла успешно!\n\n"
        "✅ <b>Premium активирован</b> — запросы теперь безлимитны.\n"
        "Каждое утро в 8:00 МСК вы будете получать прогноз на день 🌅",
        parse_mode="HTML",
    )
