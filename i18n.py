"""
Строки интерфейса на двух языках.
Использование: from i18n import t; t(lang, "key")
"""

STRINGS = {
    # ── /start ──────────────────────────────────────────────────────────
    "choose_lang": {
        "ru": "👋 Привет! Выберите язык / Choose language:",
        "en": "👋 Hi! Choose language:",
    },
    "enter_city": {
        "ru": "🏙 Введите название вашего города (на русском или английском):",
        "en": "🏙 Enter your city name:",
    },
    "welcome_back": {
        "ru": "👋 С возвращением! Ваш город: <b>{city}</b>.\n\n"
              "Команды:\n"
              "/now — погода сейчас\n"
              "/city — сменить город\n"
              "/subscribe — Premium подписка",
        "en": "👋 Welcome back! Your city: <b>{city}</b>.\n\n"
              "Commands:\n"
              "/now — current weather\n"
              "/city — change city\n"
              "/subscribe — Premium subscription",
    },
    "city_saved": {
        "ru": "✅ Город <b>{city}</b> сохранён!\n\n"
              "/now — погода сейчас\n"
              "/subscribe — Premium\n\n"
              "Каждое утро в 8:00 МСК буду присылать прогноз на день 🌅",
        "en": "✅ City <b>{city}</b> saved!\n\n"
              "/now — current weather\n"
              "/subscribe — Premium\n\n"
              "Every morning at 8:00 MSK I'll send you the daily forecast 🌅",
    },
    "city_not_found": {
        "ru": "❌ Город <b>{city}</b> не найден. Проверьте написание и попробуйте снова:",
        "en": "❌ City <b>{city}</b> not found. Check the spelling and try again:",
    },
    "checking_city": {
        "ru": "🔍 Проверяю город...",
        "en": "🔍 Checking city...",
    },
    "enter_new_city": {
        "ru": "🏙 Введите новое название города:",
        "en": "🏙 Enter new city name:",
    },
    "set_city_first": {
        "ru": "Сначала укажите город — /start",
        "en": "Please set your city first — /start",
    },

    # ── лимиты ──────────────────────────────────────────────────────────
    "limit_reached": {
        "ru": "🚫 Использованы все <b>{limit}</b> бесплатных запроса сегодня.\n\n"
              "💎 Подписка за <b>{price} ⭐ Stars</b> — безлимитный доступ.\n"
              "👇 /subscribe",
        "en": "🚫 You've used all <b>{limit}</b> free requests today.\n\n"
              "💎 Subscribe for <b>{price} ⭐ Stars</b> — unlimited access.\n"
              "👇 /subscribe",
    },
    "limit_warning": {
        "ru": "⚠️ Осталось <b>{remaining}</b> бесплатных запросов на сегодня. /subscribe",
        "en": "⚠️ <b>{remaining}</b> free requests left today. /subscribe",
    },

    # ── /now ────────────────────────────────────────────────────────────
    "now_header": {
        "ru": "🌡 <b>Погода сейчас — {city}</b>",
        "en": "🌡 <b>Current weather — {city}</b>",
    },
    "now_temp": {
        "ru": "🌡 Температура: <b>{temp:+}°C</b>  (ощущается как {feels:+}°)",
        "en": "🌡 Temperature: <b>{temp:+}°C</b>  (feels like {feels:+}°)",
    },
    "now_humidity": {
        "ru": "💧 Влажность: {humid}%",
        "en": "💧 Humidity: {humid}%",
    },
    "now_wind": {
        "ru": "💨 Ветер: {speed} м/с, {dir}",
        "en": "💨 Wind: {speed} m/s, {dir}",
    },
    "now_rain_yes": {
        "ru": "🌧 Идут осадки",
        "en": "🌧 Precipitation now",
    },
    "now_rain_no": {
        "ru": "🌂 Осадков нет",
        "en": "🌂 No precipitation",
    },
    "now_outfit_header": {
        "ru": "🧥 <b>Что надеть:</b>",
        "en": "🧥 <b>What to wear:</b>",
    },
    "next_hour_header": {
        "ru": "⏱ <b>Прогноз на ближайший час</b>",
        "en": "⏱ <b>Next hour forecast</b>",
    },
    "no_forecast": {
        "ru": "Нет данных прогноза.",
        "en": "No forecast data available.",
    },
    "error_weather": {
        "ru": "⚠️ Не удалось получить данные. Попробуйте позже.",
        "en": "⚠️ Failed to fetch weather data. Try again later.",
    },

    # ── /subscribe ───────────────────────────────────────────────────────
    "already_premium": {
        "ru": "✅ У вас уже активна Premium подписка!",
        "en": "✅ You already have an active Premium subscription!",
    },
    "subscribe_text": {
        "ru": "💎 <b>Premium подписка</b>\n\n"
              "Использовано сегодня: {used}/{limit}\n\n"
              "Что входит:\n"
              "• Безлимитные запросы /now\n"
              "• Утренний прогноз каждый день\n\n"
              "Стоимость: <b>{price} ⭐ Telegram Stars</b>\n\n"
              "👇 Нажмите кнопку для оплаты:",
        "en": "💎 <b>Premium subscription</b>\n\n"
              "Used today: {used}/{limit}\n\n"
              "Includes:\n"
              "• Unlimited /now requests\n"
              "• Daily morning forecast\n\n"
              "Price: <b>{price} ⭐ Telegram Stars</b>\n\n"
              "👇 Press the button to pay:",
    },
    "pay_button": {
        "ru": "⭐ Оплатить {price} Stars",
        "en": "⭐ Pay {price} Stars",
    },
    "invoice_title": {
        "ru": "🌤 WeatherBot Premium",
        "en": "🌤 WeatherBot Premium",
    },
    "invoice_desc": {
        "ru": "Безлимитный доступ к прогнозам погоды",
        "en": "Unlimited weather forecast access",
    },
    "payment_success": {
        "ru": "🎉 Оплата прошла успешно!\n\n"
              "✅ <b>Premium активирован</b> — запросы теперь безлимитны.\n"
              "Каждое утро в 8:00 МСК — прогноз на день 🌅",
        "en": "🎉 Payment successful!\n\n"
              "✅ <b>Premium activated</b> — unlimited requests.\n"
              "Every morning at 8:00 MSK — daily forecast 🌅",
    },

    # ── утренняя рассылка ────────────────────────────────────────────────
    "morning_header": {
        "ru": "🌅 <b>Доброе утро!</b>\n\n📍 <b>{city}</b>",
        "en": "🌅 <b>Good morning!</b>\n\n📍 <b>{city}</b>",
    },
    "morning_outfit_header": {
        "ru": "🧥 <b>ЧТО НАДЕТЬ:</b>",
        "en": "🧥 <b>WHAT TO WEAR:</b>",
    },
    "morning_no_forecast": {
        "ru": "Не удалось получить прогноз 😔",
        "en": "Failed to get forecast 😔",
    },

    # ── периоды дня ──────────────────────────────────────────────────────
    "period_morning": {
        "ru": "☀️ Утро (8:00–11:00)",
        "en": "☀️ Morning (8:00–11:00)",
    },
    "period_day": {
        "ru": "🌤 День (12:00–17:00)",
        "en": "🌤 Day (12:00–17:00)",
    },
    "period_evening": {
        "ru": "🌙 Вечер (18:00–21:00)",
        "en": "🌙 Evening (18:00–21:00)",
    },
    "period_night": {
        "ru": "🌃 Ночь",
        "en": "🌃 Night",
    },

    # ── советы по одежде ─────────────────────────────────────────────────
    # Базовые аутфиты по температуре
    "outfit_hot": {          # >= 30
        "ru": "футболку, шорты и лёгкую обувь",
        "en": "a t-shirt, shorts and light footwear",
    },
    "outfit_warm": {         # >= 23
        "ru": "футболку и лёгкие брюки или джинсы",
        "en": "a t-shirt and light trousers or jeans",
    },
    "outfit_comfortable": {  # >= 18
        "ru": "футболку и тонкую кофту",
        "en": "a t-shirt and a light sweater",
    },
    "outfit_cool": {         # >= 12
        "ru": "ветровку или лёгкую куртку поверх лонгслива",
        "en": "a windbreaker or light jacket over a long-sleeve",
    },
    "outfit_chilly": {       # >= 5
        "ru": "тёплую куртку, джинсы и закрытую обувь",
        "en": "a warm jacket, jeans and closed shoes",
    },
    "outfit_cold": {         # >= -5
        "ru": "зимнюю куртку, тёплые брюки и шапку",
        "en": "a winter jacket, warm trousers and a hat",
    },
    "outfit_very_cold": {    # >= -15
        "ru": "пуховик, шапку, шарф и тёплые перчатки",
        "en": "a down jacket, hat, scarf and warm gloves",
    },
    "outfit_extreme": {      # < -15
        "ru": "максимально тёплую одежду — мороз экстремальный!",
        "en": "maximum warm clothing — extreme frost!",
    },

    # Дополнения к аутфиту
    "extra_umbrella": {
        "ru": "не забудь зонт ☂️",
        "en": "don't forget an umbrella ☂️",
    },
    "extra_raincoat": {
        "ru": "лучше надень дождевик или возьми зонт 🌧",
        "en": "better wear a raincoat or take an umbrella 🌧",
    },
    "extra_wind": {
        "ru": "ветрено — оденься теплее 💨",
        "en": "it's windy — dress warmer 💨",
    },
    "extra_wind_strong": {
        "ru": "сильный ветер — застегнись и надень шарф 🌬",
        "en": "strong wind — button up and wear a scarf 🌬",
    },
    "extra_sun": {
        "ru": "солнечно — возьми солнцезащитные очки 😎",
        "en": "sunny — grab your sunglasses 😎",
    },
    "extra_hot": {
        "ru": "жарко — пей больше воды 💧",
        "en": "it's hot — stay hydrated 💧",
    },
    "extra_snow": {
        "ru": "идёт снег — надень нескользящую обувь ❄️",
        "en": "it's snowing — wear non-slip shoes ❄️",
    },
    "wear_prefix": {
        "ru": "Надень",
        "en": "Wear",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Возвращает строку на нужном языке с подстановкой параметров."""
    lang = lang if lang in ("ru", "en") else "ru"
    template = STRINGS.get(key, {}).get(lang, f"[{key}]")
    return template.format(**kwargs) if kwargs else template
