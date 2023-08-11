# constants.py

from __future__ import annotations

import os
from typing import NewType

import httpx
from dotenv import load_dotenv

load_dotenv()

# others
UserHitEscapeCode = NewType("UserHitEscapeCode", int)
TITLE_MAX_LENGTH = 50

# api urls
TWITCH_STREAM_BASE_URL = httpx.URL("https://www.twitch.tv/")
TWITCH_CHAT_BASE_URL = httpx.URL("https://www.twitch.tv/popout/")
TWITCH_API_BASE_URL = httpx.URL("https://api.twitch.tv/helix/")

# api credentials
TWITCH_ACCESS_TOKEN = os.environ.get("TWITCH_ACCESS_TOKEN")
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_USER_ID = os.environ.get("TWITCH_USER_ID")

# ui
BACK: str = "\u21B6"
BULLET_ICON: str = "\u2022"
CALENDAR: str = "\U0001F4C5"
CIRCLE: str = "\u25CF"
CLOCK: str = "\U0001F559"
CROSS: str = "\u2716"
DELIMITER: str = "\u2014"
EXIT: str = "\uf842"
EYE: str = "\U0001F441"
HEART: str = "\u2665"
BELL: str = "\uf0f3"
UNBELL: str = "\uf1f6"
HYPHEN_BULLET: str = "\u2043"
NOBREAK_SPACE: str = "\u00A0"
MIDDLE_DOT: str = "\u00B7"
BROKEN_BAR: str = "\u00A6"

# icons
LIVE_ICON = CIRCLE
SEPARATOR = f" {MIDDLE_DOT} "

# colors
RED: str = "#CC241D"
MAGENTA: str = "#BB9AF7"
CYAN: str = "#7DCFFF"
LIVE_ICON_COLOR = RED
