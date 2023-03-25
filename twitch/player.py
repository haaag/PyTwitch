# player.py
from __future__ import annotations

import shutil
import subprocess
import typing
from typing import Protocol

from twitch.datatypes import ExecutableNotFoundError
from twitch.utils.helpers import secure_split

if typing.TYPE_CHECKING:
    from httpx import URL


class Player(Protocol):
    name: str

    @property
    def bin(self) -> str:
        ...

    def play(self, url: str | URL) -> int:
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

    def play(self, url: str | URL) -> int:
        args = secure_split(f"{self.bin} {self.player} {url} {self.quality} {self.disable_ads}")
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

    def play(self, url: str | URL) -> int:
        args = secure_split(f"{self.bin} {url}")
        subprocess.call(args, stderr=subprocess.DEVNULL)
        return 0


def get_player(name: str) -> Player:
    players: dict[str, Player] = {
        "streamlink": StreamLink(),
        "mpv": Mpv(),
    }
    return players[name]
