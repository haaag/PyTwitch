from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING
from typing import NamedTuple

import yaml

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pathlib import Path


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


def create_default_keybinds(config_file: Path, keybinds: str) -> None:
    data = yaml.safe_load(keybinds)
    with config_file.open(mode='w') as f:
        log.debug(f'writing default keybinds to {config_file.as_posix()!r}')
        yaml.dump(data, f, default_flow_style=False)


def ensure_configfile(filename: Path, keybinds: str) -> None:
    if not filename.parent.exists():
        log.debug(f'{filename.parent!r} does not exist. creating...')
        filename.parent.mkdir()
    if not filename.exists():
        create_default_keybinds(filename, keybinds)


@functools.lru_cache
def get_keybinds(configfile: Path, keybinds: str) -> Keys:
    ensure_configfile(configfile, keybinds)
    with configfile.open(mode='r') as f:
        log.debug(f'reading keybinds from {configfile.as_posix()!r}')
        data = yaml.safe_load(f)
    return Keys(**data['keybinds'])
