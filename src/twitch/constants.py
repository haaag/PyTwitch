# constants.py

from __future__ import annotations

import os
from typing import Text

import httpx

# others
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
BACK: Text = "\u21B6"
BULLET_ICON: Text = "\u2022"
CALENDAR: Text = "\U0001F4C5"
CIRCLE: Text = "\u25CF"
CLOCK: Text = "\U0001F559"
CROSS: Text = "\u2716"
DELIMITER: Text = "\u2014"
EXIT: Text = "\uf842"
EYE: Text = "\U0001F441"
HEART: Text = "\u2665"
BELL: Text = "\uf0f3"
UNBELL: Text = "\uf1f6"
HYPHEN_BULLET: Text = "\u2043"
NOBREAK_SPACE: Text = "\u00A0"
MIDDLE_DOT: Text = "\u00B7"
BROKEN_BAR: Text = "\u00A6"

# icons
LIVE_ICON = CIRCLE
SEPARATOR = f" {MIDDLE_DOT} "

# colors
RED: str = "#CC241D"
MAGENTA: str = "#BB9AF7"
CYAN: str = "#7DCFFF"
LIVE_ICON_COLOR = RED
