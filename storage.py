"""
Работа с JSON-хранилищами:
  - user_cities.json   — города пользователей
  - user_limits.json   — счётчики запросов (сбрасываются каждый день)
  - user_premium.json  — флаги премиум-подписки
"""

import json
import os
from datetime import date
from typing import Optional

# ──────────────────────────── пути к файлам ────────────────────────────

CITIES_FILE   = "user_cities.json"
LIMITS_FILE   = "user_limits.json"
PREMIUM_FILE  = "user_premium.json"


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────── города ────────────────────────────────────

def get_city(user_id: int) -> Optional[str]:
    data = _load(CITIES_FILE)
    return data.get(str(user_id))


def set_city(user_id: int, city: str) -> None:
    data = _load(CITIES_FILE)
    data[str(user_id)] = city
    _save(CITIES_FILE, data)


def get_all_users_with_cities() -> dict:
    """Возвращает {user_id: city} для всех пользователей."""
    return _load(CITIES_FILE)


# ──────────────────────────── лимиты ────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()  # "2025-06-01"


def get_requests_today(user_id: int) -> int:
    data = _load(LIMITS_FILE)
    entry = data.get(str(user_id), {})
    if entry.get("date") != _today():
        return 0
    return entry.get("count", 0)


def increment_requests(user_id: int) -> int:
    """Увеличивает счётчик и возвращает новое значение."""
    data = _load(LIMITS_FILE)
    uid = str(user_id)
    entry = data.get(uid, {})

    if entry.get("date") != _today():
        entry = {"date": _today(), "count": 0}

    entry["count"] += 1
    data[uid] = entry
    _save(LIMITS_FILE, data)
    return entry["count"]


# ──────────────────────────── premium ───────────────────────────────────

def is_premium(user_id: int) -> bool:
    data = _load(PREMIUM_FILE)
    return data.get(str(user_id), {}).get("premium", False)


def set_premium(user_id: int) -> None:
    data = _load(PREMIUM_FILE)
    data[str(user_id)] = {"premium": True}
    _save(PREMIUM_FILE, data)
