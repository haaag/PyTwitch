# constants.py

from __future__ import annotations

import os
import pathlib
import textwrap
from typing import NewType

import httpx
from twitch.__about__ import __appname__

# paths
xdg = os.getenv('XDG_DATA_HOME', '~/.local/share')
ROOT = pathlib.Path(xdg).expanduser() / __appname__.lower()
CONFIGFILE = ROOT / 'config.yml'

# app
DESC = 'Simple tool menu for watching streams, videos from twitch.'
HELP = DESC
HELP += textwrap.dedent(
    f"""

arguments:
    -m, --menu          select menu [rofi|dmenu|fzf] (default: rofi)
    -e, --env           path to env file
    -C, --channel       search by channel query
    -G, --games         search by game or category
    -v, --verbose       increase verbosity (use -v, -vv, or -vvv)
    -h, --help          show this help

options:
    --no-markup         disable pango markup (rofi)
    --no-ansi           disable ANSI color codes (fzf)
    --no-conf           disable `mpv` configuration

files:
    config: {CONFIGFILE.as_posix()}"""
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
  group_by_categories: ctrl-t
  open_chat: ctrl-o
  search_by_game: ctrl-s
  search_by_query: ctrl-c
  show_information: ctrl-i
  show_keys: ctrl-K
  top_games: ctrl-G
  top_streams: ctrl-S
  videos: ctrl-E
  clips: ctrl-J
"""
