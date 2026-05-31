import os
from datetime import date


def _safe_replace(birth_date, year):
    # 29 февраля в невисокосный год переносим на 28 февраля.
    try:
        return birth_date.replace(year=year)
    except ValueError:
        return birth_date.replace(year=year, day=28)


def days_until_birthday(birth_date, today=None):
    """Сколько дней до ближайшего дня рождения."""
    if today is None:
        today = date.today()
    next_bd = _safe_replace(birth_date, today.year)
    if next_bd < today:
        next_bd = _safe_replace(birth_date, today.year + 1)
    return (next_bd - today).days


def upcoming(friends, within_days=30, today=None):
    """Друзья с ДР в ближайшие within_days дней, отсортированные по близости."""
    pairs = []
    for friend in friends:
        days = days_until_birthday(friend.birth_date, today=today)
        if days <= within_days:
            pairs.append((days, friend))
    pairs.sort(key=lambda pair: pair[0])
    return [friend for _, friend in pairs]
