# constants.py

from __future__ import annotations

from typing import Text

from httpx import URL

# others
TITLE_MAX_LENGTH = 50

# api
STREAM_TWITCH_BASE_URL = URL("https://www.twitch.tv/")
CHAT_TWITCH_BASE_URL = URL("https://www.twitch.tv/popout/")
API_TWITCH_BASE_URL = URL("https://api.twitch.tv/helix/")


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
