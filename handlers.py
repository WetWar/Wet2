"""
Хэндлеры бота: /start, /now, /subscribe, оплата Stars.
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
    CallbackQuery,
)

from config import settings
import storage
import weather as w
from i18n import t

logger = logging.getLogger(__name__)
router = Router()


# ─────────────────────────── FSM ────────────────────────────────────────

class Setup(StatesGroup):
    waiting_for_lang = State()
    waiting_for_city = State()


# ─────────────────────────── helpers ────────────────────────────────────

def _lang(user_id: int) -> str:
    return storage.get_lang(user_id) or "ru"


def _lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    ]])


async def check_limit(message: Message) -> bool:
    uid  = message.from_user.id
    lang = _lang(uid)

    if storage.is_premium(uid):
        return True

    used = storage.get_requests_today(uid)
    if used >= settings.FREE_DAILY_LIMIT:
        await message.answer(
            t(lang, "limit_reached",
              limit=settings.FREE_DAILY_LIMIT,
              price=settings.PREMIUM_PRICE_STARS),
            parse_mode="HTML",
        )
        return False

    storage.increment_requests(uid)
    remaining = settings.FREE_DAILY_LIMIT - used - 1
    if remaining <= 1:
        await message.answer(
            t(lang, "limit_warning", remaining=remaining),
            parse_mode="HTML",
        )
    return True


# ─────────────────────────── /start ─────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    uid  = message.from_user.id
    lang = storage.get_lang(uid)
    city = storage.get_city(uid)

    # Уже всё настроено
    if lang and city:
        await message.answer(
            t(lang, "welcome_back", city=city),
            parse_mode="HTML",
        )
        return

    # Язык ещё не выбран — спрашиваем
    await message.answer(
        t("ru", "choose_lang"),
        reply_markup=_lang_keyboard(),
    )
    await state.set_state(Setup.waiting_for_lang)


@router.callback_query(F.data.in_({"lang_ru", "lang_en"}), Setup.waiting_for_lang)
async def process_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]  # "ru" или "en"
    storage.set_lang(callback.from_user.id, lang)

    await callback.message.edit_reply_markup()  # убираем кнопки
    await callback.answer()

    await callback.message.answer(t(lang, "enter_city"))
    await state.set_state(Setup.waiting_for_city)


# ─────────────────────────── /city ──────────────────────────────────────

@router.message(Command("city"))
async def cmd_change_city(message: Message, state: FSMContext):
    lang = _lang(message.from_user.id)
    await message.answer(t(lang, "enter_new_city"))
    await state.set_state(Setup.waiting_for_city)


# ─────────────────────────── ввод города ────────────────────────────────

@router.message(Setup.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    uid        = message.from_user.id
    lang       = _lang(uid)
    city_input = message.text.strip()

    await message.answer(t(lang, "checking_city"))

    validated = await w.validate_city(city_input)
    if not validated:
        await message.answer(
            t(lang, "city_not_found", city=city_input),
            parse_mode="HTML",
        )
        return  # остаёмся в состоянии

    storage.set_city(uid, validated)
    await state.clear()

    await message.answer(
        t(lang, "city_saved", city=validated),
        parse_mode="HTML",
    )


# ─────────────────────────── /now ───────────────────────────────────────

@router.message(Command("now"))
async def cmd_now(message: Message):
    uid  = message.from_user.id
    lang = _lang(uid)
    city = storage.get_city(uid)

    if not city:
        await message.answer(t(lang, "set_city_first"))
        return

    if not await check_limit(message):
        return

    current  = await w.get_current_weather(city, lang)
    forecast = await w.get_forecast(city, lang)

    if not current:
        await message.answer(t(lang, "error_weather"))
        return

    await message.answer(
        w.format_now(current, forecast or [], lang),
        parse_mode="HTML",
    )


# ─────────────────────────── /subscribe ─────────────────────────────────

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    uid  = message.from_user.id
    lang = _lang(uid)

    if storage.is_premium(uid):
        await message.answer(t(lang, "already_premium"))
        return

    used = storage.get_requests_today(uid)
    await message.answer(
        t(lang, "subscribe_text",
          used=used,
          limit=settings.FREE_DAILY_LIMIT,
          price=settings.PREMIUM_PRICE_STARS),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=t(lang, "pay_button", price=settings.PREMIUM_PRICE_STARS),
                callback_data="pay_stars",
            )
        ]]),
    )


@router.callback_query(F.data == "pay_stars")
async def process_pay_callback(callback: CallbackQuery):
    uid  = callback.from_user.id
    lang = _lang(uid)
    await callback.answer()
    await callback.message.answer_invoice(
        title=t(lang, "invoice_title"),
        description=t(lang, "invoice_desc"),
        payload="premium_subscription",
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=settings.PREMIUM_PRICE_STARS)],
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    uid  = message.from_user.id
    lang = _lang(uid)
    storage.set_premium(uid)
    logger.info(
        "Пользователь %s оплатил Premium. payment_id=%s",
        uid, message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer(t(lang, "payment_success"), parse_mode="HTML")
