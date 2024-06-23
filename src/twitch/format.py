# format.py
from __future__ import annotations

import re
import string
from datetime import datetime
from datetime import timezone
from typing import Any


def date(dt_string: str) -> str:
    dt = datetime.fromisoformat(dt_string.rstrip('Z'))
    now = datetime.now(timezone.utc)
    if dt.date() == now.date():
        return f"Today: {dt.strftime('%H:%M')}"
    return dt.strftime('%Y-%m-%d: %H:%M')


def stringify(items: dict[str, Any], sep: str) -> list[str]:
    return [f'{k:<18}{sep}\t{v!s:<30}' for k, v in items.items()]


def date_diff_in_seconds(dt2: datetime, dt1: datetime) -> int:
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def dhms_from_seconds(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f'{days} days, {hours} hrs.'
    if hours > 0:
        return f'{hours} hrs.'
    return f'{minutes} min.'


def calculate_live_time(dt: str) -> str:
    """
    Calculates the live time of a Twitch channel.
    """
    started_at = datetime.fromisoformat(dt).replace(tzinfo=timezone.utc)
    live_since = dhms_from_seconds(date_diff_in_seconds(datetime.now(timezone.utc), started_at))
    return f'{live_since} ago'


def remove_emojis(string: str) -> str:
    emoji_pattern = re.compile(
        '['
        '\U0001F600-\U0001F64F'  # emoticons
        '\U0001F300-\U0001F5FF'  # symbols & pictographs
        '\U0001F680-\U0001F6FF'  # transport & map symbols
        '\U0001F1E0-\U0001F1FF'  # flags (iOS)
        '\U00002702-\U000027B0'
        '\U000024C2-\U0001F251'
        ']+',
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', string)


def sanitize(s: str) -> str:
    for char in '<>#%^*()_+':
        s = s.replace(char, '')
    return s.replace('&', '&amp;')


def number(number: int) -> str:
    """
    Formats the given integer number as a string with 'K' or 'M'
    suffix if >= 1000 or >= 1,000,000 respectively.
    """
    million = 1_000_000
    thousand = 1000
    if number >= million:
        return f'{number / 1_000_000:.1f}M'
    if number >= thousand:
        return f'{number / 1000:.1f}K'
    return str(number)


def remove_punctuation_escape_ampersand(s: str) -> str:
    """
    Replaces all occurrences of "&" with "&amp;" in a given string.
    """
    special_chars = string.punctuation.replace('&', '')
    s = ''.join(c for c in s if c not in special_chars)
    return s.replace('&', '&amp;')
