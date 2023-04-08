# player.py
from __future__ import annotations

import shutil
import subprocess
import typing
from typing import Protocol

from pytwitchify import helpers

if typing.TYPE_CHECKING:
    from pytwitchify.datatypes import TwitchPlayableContent


class ExecutableNotFoundError(Exception):
    pass


class Player(Protocol):
    name: str

    @property
    def bin(self) -> str:
        ...

    def play(self, item: TwitchPlayableContent) -> int:
        ...


class StreamLink:
    def __init__(self) -> None:
        self.name = "streamlink"
        self.player = "--player=mpv"
        self.quality = "best"
        self.disable_ads = "--twitch-disable-ads"

    @property
    def bin(self) -> str:
        bin = shutil.which(self.name)
        if not bin:
            raise ExecutableNotFoundError(self.name)
        return bin

    def play(self, item: TwitchPlayableContent) -> int:
        args = helpers.secure_split(f"{self.bin} {self.player} {item.url} {self.quality}")
        subprocess.call(args, stderr=subprocess.DEVNULL)
        return 0


class Mpv:
    def __init__(self) -> None:
        self.name = "mpv"

    @property
    def bin(self) -> str:
        bin = shutil.which(self.name)
        if not bin:
            raise ExecutableNotFoundError(self.name)
        return bin

    def play(self, item: TwitchPlayableContent) -> int:
        args = helpers.secure_split(f"{self.bin} {item.url}")
        subprocess.call(args, stderr=subprocess.DEVNULL)
        return 0


def create_player(name: str) -> Player:
    players: dict[str, Player] = {
        "streamlink": StreamLink(),
        "mpv": Mpv(),
    }
    return players[name]
