"""
Работа с OpenWeatherMap API (бесплатный тариф).

Используемые эндпоинты:
  - /weather  — текущая погода
  - /forecast — прогноз по 3-часовым шагам (5 дней)

Документация: https://openweathermap.org/api
"""

import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Optional

from config import settings

BASE_URL = "https://api.openweathermap.org/data/2.5"
LANG = "ru"
UNITS = "metric"  # Цельсий

# МСК = UTC+3
MSK = timezone(timedelta(hours=3))


# ─────────────────────────── вспомогательные ────────────────────────────

def _wind_dir(deg: float) -> str:
    dirs = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return dirs[round(deg / 45) % 8]


def _clothing_advice(temp: float, rain: bool, wind: float) -> str:
    """Совет по одежде на основе температуры, дождя и ветра."""
    if temp >= 25:
        outfit = "футболку и шорты"
    elif temp >= 18:
        outfit = "футболку и лёгкую кофту"
    elif temp >= 10:
        outfit = "ветровку или лёгкую куртку"
    elif temp >= 0:
        outfit = "тёплую куртку и джинсы"
    else:
        outfit = "зимнюю куртку, шапку и перчатки"

    extras = []
    if rain:
        extras.append("не забудь зонт ☂️")
    if wind > 8 and temp < 15:
        extras.append("ветрено — оденься теплее 💨")

    advice = f"Надень {outfit}."
    if extras:
        advice += " " + ", ".join(extras).capitalize() + "."
    return advice


def _period_label(hour: int) -> str:
    if 8 <= hour < 12:
        return "☀️ Утро (8:00–11:00)"
    if 12 <= hour < 18:
        return "🌤 День (12:00–17:00)"
    if 18 <= hour < 22:
        return "🌙 Вечер (18:00–21:00)"
    return "🌃 Ночь"


# ─────────────────────────── API-запросы ────────────────────────────────

async def validate_city(city: str) -> Optional[str]:
    """
    Проверяет существование города через API.
    Возвращает корректное имя города (как оно хранится в OWM) или None.
    """
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": LANG,
        "units": UNITS,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/weather", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["name"]  # OWM-имя города на русском
            return None


async def get_current_weather(city: str) -> Optional[dict]:
    """Текущая погода."""
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": LANG,
        "units": UNITS,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/weather", params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def get_forecast(city: str) -> Optional[list]:
    """
    Прогноз на 5 дней с шагом 3 часа.
    Возвращает список точек прогноза.
    """
    params = {
        "q": city,
        "appid": settings.OWM_API_KEY,
        "lang": LANG,
        "units": UNITS,
        "cnt": 16,  # 16 × 3ч = 48 часов — достаточно для дня и завтра
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/forecast", params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("list", [])


# ─────────────────────────── форматирование ─────────────────────────────

def format_current(data: dict) -> str:
    """Форматирует текущую погоду для команды /now."""
    city    = data["name"]
    temp    = round(data["main"]["temp"])
    feels   = round(data["main"]["feels_like"])
    humid   = data["main"]["humidity"]
    desc    = data["weather"][0]["description"].capitalize()
    wind_sp = data["wind"]["speed"]
    wind_dg = data["wind"].get("deg", 0)

    # Есть ли дождь/снег прямо сейчас?
    rain = "rain" in data or "snow" in data

    advice = _clothing_advice(temp, rain, wind_sp)

    return (
        f"🌡 <b>Погода сейчас — {city}</b>\n\n"
        f"🌡 Температура: <b>{temp:+}°C</b>  (ощущается как {feels:+}°)\n"
        f"💧 Влажность: {humid}%\n"
        f"💨 Ветер: {wind_sp} м/с, {_wind_dir(wind_dg)}\n"
        f"☁️ {desc}\n"
        f"{'🌧 Идут осадки' if rain else '🌂 Осадков нет'}\n\n"
        f"🧥 <b>Что надеть:</b> {advice}"
    )


def format_hourly(forecast: list) -> str:
    """Форматирует прогноз на ближайшие 2 часа (первые 2 точки) для /hourly."""
    if not forecast:
        return "Нет данных прогноза."

    # Берём первые 2 временны́е точки (≈ сейчас и +3ч)
    lines = ["⏱ <b>Почасовой прогноз</b>\n"]
    for item in forecast[:2]:
        dt    = datetime.fromtimestamp(item["dt"], tz=MSK)
        temp  = round(item["main"]["temp"])
        desc  = item["weather"][0]["description"].capitalize()
        wind  = item["wind"]["speed"]
        rain  = item.get("pop", 0) > 0.3  # вероятность осадков > 30%
        pop   = round(item.get("pop", 0) * 100)

        lines.append(
            f"🕐 <b>{dt:%H:%M}</b> — {temp:+}°C, {desc}\n"
            f"   💨 {wind} м/с  |  🌧 Осадки: {pop}%"
        )

    # Совет по ближайшему часу
    first = forecast[0]
    advice = _clothing_advice(
        round(first["main"]["temp"]),
        first.get("pop", 0) > 0.3,
        first["wind"]["speed"],
    )
    lines.append(f"\n🧥 <b>Что надеть:</b> {advice}")

    return "\n".join(lines)


def format_morning_digest(city: str, forecast: list) -> str:
    """
    Форматирует утреннюю рассылку.
    Группирует точки прогноза по периодам дня.
    """
    if not forecast:
        return "Не удалось получить прогноз 😔"

    # Фильтруем точки на сегодня по МСК
    today = datetime.now(MSK).date()
    periods: dict[str, list] = {}

    for item in forecast:
        dt = datetime.fromtimestamp(item["dt"], tz=MSK)
        if dt.date() != today:
            continue
        period = _period_label(dt.hour)
        periods.setdefault(period, []).append(item)

    if not periods:
        # Если рассылка идёт ночью и "сегодня" нет точек — берём первые из списка
        for item in forecast[:6]:
            dt = datetime.fromtimestamp(item["dt"], tz=MSK)
            period = _period_label(dt.hour)
            periods.setdefault(period, []).append(item)

    lines = [f"🌅 <b>Доброе утро!</b>\n\n📍 <b>{city}</b>\n"]

    all_temps, all_rains, all_winds = [], [], []

    for period_name, items in periods.items():
        avg_temp = round(sum(i["main"]["temp"] for i in items) / len(items))
        desc     = items[0]["weather"][0]["description"].capitalize()
        avg_wind = round(sum(i["wind"]["speed"] for i in items) / len(items), 1)
        avg_pop  = sum(i.get("pop", 0) for i in items) / len(items)

        rain_str = f", дождь {round(avg_pop*100)}%" if avg_pop > 0.3 else ""
        lines.append(f"{period_name}: <b>{avg_temp:+}°</b>, {desc}, ветер {avg_wind} м/с{rain_str}")

        all_temps.append(avg_temp)
        all_rains.append(avg_pop > 0.3)
        all_winds.append(avg_wind)

    # Совет по одежде — по средней за день
    if all_temps:
        day_temp  = sum(all_temps) / len(all_temps)
        day_rain  = any(all_rains)
        day_wind  = max(all_winds)
        advice    = _clothing_advice(round(day_temp), day_rain, day_wind)
        lines.append(f"\n🧥 <b>ЧТО НАДЕТЬ:</b>\n{advice}")

    return "\n".join(lines)
