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

arguments:
    -m, --menu          select menu [rofi|dmenu] (default: rofi)
    -e, --env           path to env file
    -C, --channel       search by channel query
    -G, --games         search by game or category
    -v, --verbose       increase verbosity (use -v, -vv, or -vvv)
    -h, --help          show this help

options:
    --no-markup         disable pango markup (rofi)
    --no-ansi           disable ANSI color codes (fzf)
    --no-conf           disable `mpv` configuration
    """
)

# others
UserCancel = NewType('UserCancel', int)
UserConfirms = NewType('UserConfirms', int)
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

# keybinds
DEFAULT_KEYBINDS = """
keybinds:
  group_by_categories: alt-t
  show_information: alt-i
  open_chat: alt-o
  show_keys: alt-k
  search_by_game: alt-s
  search_by_query: alt-c
  top_streams: alt-m
  top_games: alt-g
  videos: alt-v
  clips: alt-C
"""
