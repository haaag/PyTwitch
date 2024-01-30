# player.py
from __future__ import annotations

import logging
import shutil
import subprocess
import typing

from twitch import helpers
from twitch._exceptions import ExecutableNotFoundError

log = logging.getLogger(__name__)


class TwitchPlayableContent(typing.Protocol):
    url: str


class Player:
    def __init__(self, name: str = "player") -> None:
        self.name = name
        self.options: list[str] = []

    @property
    def bin(self) -> str:
        bin = shutil.which(self.name)
        if not bin:
            err_msg = f"player={self.name!r} not found"
            log.error(err_msg)
            raise ExecutableNotFoundError(err_msg)
        return bin

    def add_options(self, args: str) -> None:
        log.debug("adding player args: %s", args)
        args_split = helpers.secure_split(args)
        self.options.extend(args_split)

    def args(self, url: str) -> list[str]:
        args = [self.bin, url]
        args.extend(self.options)
        return args

    def play(self, item: TwitchPlayableContent) -> subprocess.Popen:
        args = self.args(item.url)
        log.info("executing: %s", args)
        return subprocess.Popen(args, stderr=subprocess.DEVNULL)


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


class Mpv(Player):
    def __init__(self, name: str = "mpv") -> None:
        self.name = name
        super().__init__()


PLAYERS: dict[str, Player] = {}


class FactoryPlayer:
    @staticmethod
    def create(name: str) -> Player:
        return PLAYERS.get(name, Player(name))

    @staticmethod
    def register(player: Player) -> None:
        PLAYERS[player.name] = player


FactoryPlayer.register(Mpv())
FactoryPlayer.register(StreamLink())


# TODO:
# streamlink --record path/to/file.ts example.com/stream best
# streamlink --player mpv --player-args '--no-border --no-keepaspect-window' twitch.tv/CHANNEL 1080p60
# streamlink --twitch-low-latency -p mpv -a '--cache=yes --demuxer-max-back-bytes=2G' twitch.tv/CHANNEL best
