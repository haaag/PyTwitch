# player.py
from __future__ import annotations

import logging
import shutil
import subprocess
import typing

from pytwitchify import helpers

if typing.TYPE_CHECKING:
    from pytwitchify.datatypes import TwitchPlayableContent


log = logging.getLogger(__name__)


class ExecutableNotFoundError(Exception):
    pass


class Player:
    def __init__(self, name: str = "player") -> None:
        self.name = name

    @property
    def bin(self) -> str:
        bin = shutil.which(self.name)
        if not bin:
            raise ExecutableNotFoundError(self.name)
        return bin

    def args(self, url: str) -> list[str]:
        return [self.bin, url]

    def play(self, item: TwitchPlayableContent) -> int:
        return subprocess.call(self.args(item.url), stderr=subprocess.DEVNULL)


class StreamLink(Player):
    def __init__(self, name: str = "streamlink") -> None:
        self.name = name

    def args(self, url: str) -> list[str]:
        player = "--player=mpv"
        quality = "best"
        return helpers.secure_split(f"{self.bin} {player} {url} {quality}")


class Mpv(Player):
    def __init__(self, name: str = "mpv") -> None:
        self.name = name


def create_player(name: str) -> Player:
    players: dict[str, Player] = {
        "streamlink": StreamLink(),
        "mpvs": Mpv(),
    }
    return players.pop(name, Player(name))
