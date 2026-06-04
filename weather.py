"""
Работа с OpenWeatherMap API (бесплатный тариф).

Используемые эндпоинты:
  - /weather  — текущая погода
  - /forecast — прогноз по 3-часовым шагам (5 дней)
"""

import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import settings
from i18n import t

BASE_URL = "https://api.openweathermap.org/data/2.5"
UNITS = "metric"

MSK = timezone(timedelta(hours=3))

WIND_DIRS_RU = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
WIND_DIRS_EN = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


# ─────────────────────────── вспомогательные ────────────────────────────

def _wind_dir(deg: float, lang: str) -> str:
    dirs = WIND_DIRS_RU if lang == "ru" else WIND_DIRS_EN
    return dirs[round(deg / 45) % 8]


def _clothing_advice(temp: float, rain: bool, snow: bool, wind: float,
                     sunny: bool, lang: str) -> str:
    """
    Детальный совет по одежде.
    Учитывает температуру, осадки, ветер и солнце.
    """
    # Базовый аутфит по температуре
    if temp >= 30:
        outfit_key = "outfit_hot"
    elif temp >= 23:
        outfit_key = "outfit_warm"
    elif temp >= 18:
        outfit_key = "outfit_comfortable"
    elif temp >= 12:
        outfit_key = "outfit_cool"
    elif temp >= 5:
        outfit_key = "outfit_chilly"
    elif temp >= -5:
        outfit_key = "outfit_cold"
    elif temp >= -15:
        outfit_key = "outfit_very_cold"
    else:
        outfit_key = "outfit_extreme"

    extras = []

    # Осадки
    if snow:
        extras.append(t(lang, "extra_snow"))
    elif rain:
        if wind > 8:
            extras.append(t(lang, "extra_raincoat"))
        else:
            extras.append(t(lang, "extra_umbrella"))

    # Ветер
    if wind > 15:
        extras.append(t(lang, "extra_wind_strong"))
    elif wind > 8 and temp < 15 and not rain:
        extras.append(t(lang, "extra_wind"))

    # Солнце и жара
    if sunny and temp >= 20:
        extras.append(t(lang, "extra_sun"))
    if temp >= 30:
        extras.append(t(lang, "extra_hot"))

    prefix = t(lang, "wear_prefix")
    advice = f"{prefix} {t(lang, outfit_key)}."
    if extras:
        advice += " " + ", ".join(extras).capitalize() + "."
    return advice


def _period_key(hour: int) -> str:
    if 8 <= hour < 12:
        return "period_morning"
    if 12 <= hour < 18:
        return "period_day"
    if 18 <= hour < 22:
        return "period_evening"
    return "period_night"


def _owm_lang(lang: str) -> str:
    return "ru" if lang == "ru" else "en"


# ─────────────────────────── API-запросы ────────────────────────────────

async def validate_city(city: str) -> Optional[str]:
    """Проверяет город, возвращает OWM-имя или None."""
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": "ru",
        "units": UNITS,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/weather", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["name"]
            return None


async def get_current_weather(city: str, lang: str = "ru") -> Optional[dict]:
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": _owm_lang(lang),
        "units": UNITS,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/weather", params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def get_forecast(city: str, lang: str = "ru") -> Optional[list]:
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": _owm_lang(lang),
        "units": UNITS,
        "cnt": 16,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/forecast", params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("list", [])


# ─────────────────────────── форматирование ─────────────────────────────

def format_now(current: dict, forecast: list, lang: str) -> str:
    """
    /now: текущая погода + прогноз на ближайший час + совет по одежде.
    """
    city   = current["name"]
    temp   = round(current["main"]["temp"])
    feels  = round(current["main"]["feels_like"])
    humid  = current["main"]["humidity"]
    desc   = current["weather"][0]["description"].capitalize()
    wind_s = current["wind"]["speed"]
    wind_d = current["wind"].get("deg", 0)
    rain   = "rain" in current
    snow   = "snow" in current
    sunny  = current["weather"][0]["icon"].endswith("d") and current["weather"][0]["id"] in range(800, 803)

    advice = _clothing_advice(temp, rain, snow, wind_s, sunny, lang)

    lines = [
        t(lang, "now_header", city=city),
        "",
        t(lang, "now_temp", temp=temp, feels=feels),
        t(lang, "now_humidity", humid=humid),
        t(lang, "now_wind", speed=wind_s, dir=_wind_dir(wind_d, lang)),
        f"☁️ {desc}",
        t(lang, "now_rain_yes") if (rain or snow) else t(lang, "now_rain_no"),
    ]

    # Прогноз на ближайший час из forecast
    if forecast:
        next_item = forecast[0]
        next_dt   = datetime.fromtimestamp(next_item["dt"], tz=MSK)
        next_temp = round(next_item["main"]["temp"])
        next_desc = next_item["weather"][0]["description"].capitalize()
        next_pop  = round(next_item.get("pop", 0) * 100)
        next_wind = next_item["wind"]["speed"]

        lines += [
            "",
            t(lang, "next_hour_header"),
            f"🕐 {next_dt:%H:%M} — {next_temp:+}°C, {next_desc}",
            f"💨 {next_wind} м/с  |  🌧 {next_pop}%" if lang == "ru"
            else f"💨 {next_wind} m/s  |  🌧 {next_pop}%",
        ]

    lines += ["", t(lang, "now_outfit_header"), advice]
    return "\n".join(lines)


def format_morning_digest(city: str, forecast: list, lang: str) -> str:
    """Утренняя рассылка — прогноз по периодам дня."""
    if not forecast:
        return t(lang, "morning_no_forecast")

    today = datetime.now(MSK).date()
    periods: dict[str, list] = {}

    for item in forecast:
        dt = datetime.fromtimestamp(item["dt"], tz=MSK)
        if dt.date() != today:
            continue
        key = _period_key(dt.hour)
        periods.setdefault(key, []).append(item)

    if not periods:
        for item in forecast[:6]:
            dt = datetime.fromtimestamp(item["dt"], tz=MSK)
            key = _period_key(dt.hour)
            periods.setdefault(key, []).append(item)

    lines = [t(lang, "morning_header", city=city), ""]

    all_temps, all_rains, all_snows, all_winds, all_sunny = [], [], [], [], []

    for period_key, items in periods.items():
        avg_temp = round(sum(i["main"]["temp"] for i in items) / len(items))
        desc     = items[0]["weather"][0]["description"].capitalize()
        avg_wind = round(sum(i["wind"]["speed"] for i in items) / len(items), 1)
        avg_pop  = sum(i.get("pop", 0) for i in items) / len(items)
        has_snow = any("snow" in i for i in items)

        rain_str = ""
        if avg_pop > 0.3:
            pct = round(avg_pop * 100)
            rain_str = f", ❄️ {pct}%" if has_snow else f", 🌧 {pct}%"

        lines.append(
            f"{t(lang, period_key)}: <b>{avg_temp:+}°</b>, {desc}, "
            f"{'💨'} {avg_wind} {'м/с' if lang == 'ru' else 'm/s'}{rain_str}"
        )

        all_temps.append(avg_temp)
        all_rains.append(avg_pop > 0.3 and not has_snow)
        all_snows.append(has_snow)
        all_winds.append(avg_wind)
        all_sunny.append(items[0]["weather"][0]["icon"].endswith("d"))

    if all_temps:
        advice = _clothing_advice(
            round(sum(all_temps) / len(all_temps)),
            any(all_rains),
            any(all_snows),
            max(all_winds),
            any(all_sunny),
            lang,
        )
        lines += ["", t(lang, "morning_outfit_header"), advice]

    return "\n".join(lines)
