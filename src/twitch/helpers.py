# utils.py

from __future__ import annotations

import logging
import re
import shlex
import shutil
import string
import subprocess
import time
from datetime import datetime
from datetime import timezone
from functools import wraps
from typing import Any
from typing import Callable
from typing import NamedTuple

from pyselector import Menu

log = logging.getLogger(__name__)


class Clipboard(NamedTuple):
    copy: str
    paste: str


def get_clipboard() -> Clipboard:
    # TODO: [ ] add support for other platforms
    clipboards: dict[str, Clipboard] = {
        "xclip": Clipboard(
            copy="xclip -selection clipboard",
            paste="xclip -selection clipboard -o",
        ),
        "xsel": Clipboard(
            copy="xsel -b -i",
            paste="xsel -b -o",
        ),
    }
    for name, clipboard in clipboards.items():
        if shutil.which(name):
            log.info(f"clipboard command: {clipboard!r}")
            return clipboard
    err_msg = "No suitable clipboard command found."
    log.error(err_msg)
    raise FileNotFoundError(err_msg)


def copy_to_clipboard(item: str) -> int:
    """Copy selected item to the system clipboard."""
    data = item.encode("utf-8", errors="ignore")
    args = shlex.split(get_clipboard().copy)
    try:
        with subprocess.Popen(args, stdin=subprocess.PIPE) as proc:
            proc.stdin.write(data)  # type: ignore[union-attr]
            log.debug("Copied '%s' to clipboard", item)
    except subprocess.SubprocessError as e:
        log.error("Failed to copy '%s' to clipboard: %s", item, e)
        return 1
    return 0


def timeit(func: Callable) -> Callable:
    @wraps(func)
    def inner(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        log.info("execution time: '%s': %s seconds", func.__name__, elapsed)
        return result

    return inner


def stringify_dict(items: dict[str, Any], sep: str) -> list[str]:
    return [f"{str(k):<18}{sep}\t{str(v):<30}" for k, v in items.items()]


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


def extract_key_from_str(s: str, sep: str) -> str:
    log.debug("extracting from=%s", s)
    s = s.split(sep)[0]
    match = re.search(r"<span\s.*?>(.*?)</span>", s)
    if match:
        s = match.group(1)
    return s


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
    for char in "<>#%^*()_+":
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
