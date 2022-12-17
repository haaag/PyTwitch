# utils.py

import re
from datetime import datetime


def date_diff_in_seconds(dt2: datetime, dt1: datetime) -> int:
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def dhms_from_seconds(seconds: int):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f"{days} days, {hours} hrs."
    elif hours > 0:
        return f"{hours} hrs."
    else:
        return f"{minutes} min."


def calculate_live_time(dt: str) -> str:
    started_at = datetime.fromisoformat(dt).replace(tzinfo=None)
    live_since = dhms_from_seconds(date_diff_in_seconds(datetime.utcnow(), started_at))
    return f"Live: {live_since} ago"


def remove_emojis(string: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", string)
