# player.py
from __future__ import annotations

import logging
import shutil
import subprocess
import typing
from datetime import datetime
from datetime import timezone
from pathlib import Path

from src.twitch import helpers

log = logging.getLogger(__name__)


class ExecutableNotFoundError(Exception):
    pass


class TwitchPlayableContent(typing.Protocol):
    name: str
    url: str
    chat: str


class Player:
    def __init__(self, name: str = "player") -> None:
        self.name = name
        self.options: list[str] = []

    @property
    def bin(self) -> str:
        bin = shutil.which(self.name)
        if not bin:
            raise ExecutableNotFoundError(self.name)
        return bin

    def add_options(self, args: str) -> None:
        log.debug("adding player args: %s", args)
        args_splitted = helpers.secure_split(args)
        self.options.extend(args_splitted)

    def args(self, url: str) -> list[str]:
        args = [self.bin, url]
        args.extend(self.options)
        return args

    def play(self, item: TwitchPlayableContent) -> int:
        args = self.args(item.url)
        log.info("executing: %s", args)
        return subprocess.call(args, stderr=subprocess.DEVNULL)

    def record(self, item: TwitchPlayableContent, path: str) -> int:
        raise NotImplementedError


class StreamLink(Player):
    def __init__(self, name: str = "streamlink") -> None:
        self.name = name
        self.player = "--player=mpv"
        self.quality = "best"
        super().__init__(self.name)

    def args(self, url: str) -> list[str]:
        args = [self.bin]
        args.extend([self.player, url, self.quality])
        args.extend(self.options)
        return args

    def record(self, item: TwitchPlayableContent, path: str) -> int:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = Path(path).expanduser() / f"{now}_{item.name}.ts"
        args = [self.bin, self.player, "--record", str(filepath), item.url, self.quality]
        return subprocess.call(args, stderr=subprocess.DEVNULL)


class Mpv(Player):
    def __init__(self, name: str = "mpv") -> None:
        self.name = name
        super().__init__()


def create_player(name: str) -> Player:
    players: dict[str, Player] = {
        "streamlink": StreamLink(),
        "mpvs": Mpv(),
    }
    return players.get(name, Player(name))


# TODO:
# streamlink --record path/to/file.ts example.com/stream best
# streamlink --player mpv --player-args '--no-border --no-keepaspect-window' twitch.tv/CHANNEL 1080p60
# streamlink --twitch-low-latency -p mpv -a '--cache=yes --demuxer-max-back-bytes=2G' twitch.tv/CHANNEL best
