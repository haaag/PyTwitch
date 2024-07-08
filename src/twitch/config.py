from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import NamedTuple

import yaml
from twitch import constants
from twitch.__about__ import __appname__


class Keys(NamedTuple):
    group_by_categories: str
    show_information: str
    open_chat: str
    show_keys: str
    search_by_game: str
    search_by_query: str
    # Content
    top_streams: str
    top_games: str
    videos: str
    clips: str


def create_default_keybinds(config_file: Path) -> None:
    data = yaml.safe_load(constants.DEFAULT_KEYBINDS)
    with config_file.open(mode='w') as f:
        yaml.dump(data, f)


def get_config_file() -> Path:
    xdg_env = os.getenv('XDG_DATA_HOME', '~/.local/share')
    root = Path(xdg_env).expanduser() / __appname__.lower()

    if not root.exists():
        root.mkdir()

    configfile = root / 'config.yml'

    if not configfile.exists():
        create_default_keybinds(configfile)

    return configfile


@functools.lru_cache
def get_keybinds() -> Keys:
    configfile = get_config_file()
    with configfile.open(mode='r') as f:
        data = yaml.safe_load(f)
    return Keys(**data['keybinds'])
