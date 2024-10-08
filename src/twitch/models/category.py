# category.py

from __future__ import annotations

from pydantic.dataclasses import dataclass
from pyselector.colors import Color
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import LIVE_ICON
from twitch.models.channels import FollowedChannelInfo  # noqa: TCH002
from twitch.models.streams import FollowedStream  # noqa: TCH002


@dataclass
class Category:
    name: str
    channels: dict[str, FollowedStream | FollowedChannelInfo]
    markup: bool = True
    playable: bool = False
    ansi: bool = False

    def __hash__(self) -> int:
        return hash(self.name)

    def channels_live(self) -> int:
        return sum(1 for c in self.channels.values() if c.live)

    def total_viewers(self) -> int:
        return sum(c.viewer_count for c in self.channels.values())

    def live(self) -> bool:
        return self.channels_live() > 0

    def total_viewers_fmt(self) -> str:
        if self.channels_live() == 0:
            return ''
        return format.number(self.total_viewers())

    def total_channels(self) -> int:
        return len(self.channels)

    def viewers_fmt(self) -> str:
        if self.channels_live() == 0:
            return ''
        return PangoSpan(
            f'{format.number(self.total_viewers())} viewers',
            font_variant='small-caps',
            size='small',
            weight='bold',
            foreground=Color.yellow(),
            fg_ansi='yellow',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def online_fmt(self) -> str:
        nlive = self.channels_live()
        if nlive == 0:
            return ''
        live = f'{LIVE_ICON} {nlive}'
        return PangoSpan(
            live,
            foreground=Color.red(),
            fg_ansi='red',
            size='medium',
            weight='heavy',
            markup=self.markup,
            ansi=self.ansi,
        )

    def offline_fmt(self) -> str:
        return PangoSpan(
            f'{LIVE_ICON} Offline',
            foreground=Color.grey(),
            fg_ansi='grey',
            size='x-large',
            sub=True,
            alpha='45%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def name_fmt(self) -> str:
        name = format.sanitize(self.name)
        return PangoSpan(name, weight='bold', size='large', fg_ansi='cyan', markup=self.markup, ansi=self.ansi)

    def online_str(self) -> str:
        return f'{self.name_fmt} {self.online_fmt} {self.viewers_fmt()}'

    def offline_str(self) -> str:
        return f'{self.name_fmt} {self.offline_fmt()}'

    def __str__(self) -> str:
        return self.online_str() if self.live() else self.offline_str()


@dataclass
class Game:
    id: str
    name: str
    box_art_url: str
    igdb_id: str | None = None
    markup: bool = False
    ansi: bool = False

    @property
    def name_str(self) -> str:
        name = format.sanitize(self.name)
        return PangoSpan(name, weight='bold', size='medium', markup=self.markup, ansi=self.ansi)

    def __str__(self) -> str:
        return f'{self.name_str}'
