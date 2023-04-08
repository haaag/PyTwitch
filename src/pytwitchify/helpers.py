# utils.py

from __future__ import annotations

import logging
import re
import shlex
import string
import sys
from datetime import datetime
from datetime import timezone
from typing import Callable

from pyselector import Menu

log = logging.getLogger(__name__)


def date_diff_in_seconds(dt2: datetime, dt1: datetime) -> int:
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def dhms_from_seconds(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f"{days} days, {hours} hrs."
    if hours > 0:
        return f"{hours} hrs."
    return f"{minutes} min."


def calculate_live_time(dt: str) -> str:
    """
    Calculates the live time of a Twitch channel.
    """
    started_at = datetime.fromisoformat(dt).replace(tzinfo=None)
    live_since = dhms_from_seconds(date_diff_in_seconds(datetime.utcnow(), started_at))
    return f"{live_since} ago"


def display_no_results_msg(mesg: str, prompt: Callable) -> int:
    log.warning(mesg)
    prompt(items=[mesg])
    sys.exit(1)


def extract_id_from_str(item: str, sep: str) -> int:
    """Extracts the ID number from a string that represents a video title."""
    if not item[0].isdigit():
        log.info("extract_id_from_str: not a valid item='%s'", item)
        raise ValueError("Not a valid item")
    return int(item.split(sep)[0])


def extract_username_from_str(stream_str: str, search_for: str) -> str:
    if not stream_str.startswith(search_for):
        return stream_str
    log.debug("extract_username_from_str '%s'", stream_str)
    return stream_str.split()[1]


def extract_str_from_span(s: str) -> str:
    log.debug("processing string '%s'", s)
    pattern = re.compile(r"<.*?>")
    string = re.sub(pattern, "", s)
    log.debug("username extracted '%s'", string.split()[0])
    return string.split()[0]


def extract_username(string: str) -> str:
    log.info("extract_username_from_span '%s'", string)
    match = re.search(r"<span\s.*?>(.*?)</span>", string)
    if match:
        log.info("username extracted: '%s'", match.group(1))
        return match.group(1)
    return string


def remove_span_and_extract_username(stream_str: str, search_for: str) -> str:
    if not stream_str.startswith(search_for):
        return stream_str
    log.debug("extract_username_from_str '%s'", stream_str)
    pattern = re.compile(r"<.*?>")
    string = re.sub(pattern, "", stream_str)
    return string.split()[1]


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


def clean_string(s):
    for char in "<>#$%^*()_+":
        s = s.replace(char, "")
    return s.replace("&", "&amp;")


def secure_split(command: str) -> list[str]:
    try:
        command_splited: list[str] = shlex.split(command)
    except ValueError:
        command = command.replace("'", "")
        command_splited = shlex.split(command)
    return command_splited


def format_number(number) -> str:
    return f"{number/1000:.1f}K" if int(number) >= 1000 else str(number)


def remove_punctuation_escape_ampersand(s: str) -> str:
    """
    Replaces all occurrences of "&" with "&amp;" in a given string.
    """
    special_chars = string.punctuation.replace("&", "")
    s = "".join(c for c in s if c not in special_chars)
    return s.replace("&", "&amp;")


def format_datetime(dt_string: str) -> str:
    dt = datetime.fromisoformat(dt_string.rstrip("Z"))
    now = datetime.now(timezone.utc)
    if dt.date() == now.date():
        return f"Today: {dt.strftime('%H:%M')}"
    return dt.strftime("%Y-%m-%d: %H:%M")


def get_launcher(name: str):
    launchers = {
        "rofi": Menu.rofi(),
        "dmenu": Menu.dmenu(),
        "fzf": Menu.fzf(),
    }
    return launchers[name]


def sort_by_key(key: str, items: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(items, key=lambda x: x[key])
