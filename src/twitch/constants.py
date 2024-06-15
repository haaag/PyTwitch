# constants.py

from __future__ import annotations

import textwrap
from typing import NewType

import httpx

# app
DESC = 'Simple tool menu for watching streams, videos from twitch.'
HELP = DESC
HELP += textwrap.dedent(
    """

options:
    -m, --menu          select menu [rofi|dmenu] (default: rofi)
    -p, --player        select player [mpv|streamlink] (default: mpv)
    -a, --player-args   pass arguments to player
    -c, --config        path to env file
    -C, --channel       search by channel query
    -G, --games         search by game or category
    -v, --verbose       verbose mode
    -h, --help          show this help

menu options:
    --no-markup         disable pango markup (rofi)
    """
)

# others
UserCancelSelection = NewType('UserCancelSelection', int)
UserConfirmsSelection = NewType('UserConfirmsSelection', int)
TITLE_MAX_LENGTH = 80

# api urls
TWITCH_STREAM_BASE_URL = httpx.URL('https://www.twitch.tv/')
TWITCH_CHAT_BASE_URL = httpx.URL('https://www.twitch.tv/popout/')
TWITCH_API_BASE_URL = httpx.URL('https://api.twitch.tv/helix/')

# ui
BACK: str = '\u21b6'
BULLET_ICON: str = '\u2022'
CALENDAR: str = '\U0001f4c5'
CIRCLE: str = '\u25cf'
CLOCK: str = '\U0001f559'
CROSS: str = '\u2716'
DELIMITER: str = '\u2014'
EXIT: str = '\uf842'
EYE: str = '\U0001f441'
HEART: str = '\u2665'
BELL: str = '\uf0f3'
UNBELL: str = '\uf1f6'
HYPHEN_BULLET: str = '\u2043'
NOBREAK_SPACE: str = '\u00a0'
MIDDLE_DOT: str = '\u00b7'
BROKEN_BAR: str = '\u00a6'
SQUARE: str = '■'

# icons
LIVE_ICON = CIRCLE
SEPARATOR = f' {MIDDLE_DOT} '

# colors
RED: str = '#CC241D'
MAGENTA: str = '#BB9AF7'
CYAN: str = '#7DCFFF'
LIVE_ICON_COLOR = RED
