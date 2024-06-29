# category.py

from __future__ import annotations

from pydantic.dataclasses import dataclass
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import LIVE_ICON
from twitch.constants import LIVE_ICON_COLOR
from twitch.constants import SEPARATOR
from twitch.models.channels import FollowedChannelInfo  # noqa: TCH002
from twitch.models.streams import FollowedStream  # noqa: TCH002


@dataclass
class Category:
    name: str
    channels: dict[str, FollowedStream | FollowedChannelInfo]
    markup: bool = True
    playable: bool = False

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
            foreground='orange',
            markup=self.markup,
        )

    @property
    def online_fmt(self) -> str:
        nlive = self.channels_live()
        if nlive == 0:
            return ''
        live = f'{LIVE_ICON} {nlive}'
        return PangoSpan(
            live,
            foreground=LIVE_ICON_COLOR,
            size='medium',
            weight='heavy',
            markup=self.markup,
        )

    def offline_fmt(self) -> str:
        return PangoSpan(
            f'{LIVE_ICON} Offline',
            foreground='grey',
            size='x-large',
            sub=True,
            alpha='45%',
            markup=self.markup,
        )

    @property
    def name_fmt(self) -> str:
        name = format.sanitize(self.name)
        return PangoSpan(name, weight='bold', size='large', markup=self.markup)

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    def online_str(self) -> str:
        return f'{self.name_fmt}{self.sep}{self.online_fmt} {self.viewers_fmt()}'

    def offline_str(self) -> str:
        return f'{self.name_fmt}{self.sep} {self.offline_fmt()}'

    def __str__(self) -> str:
        return self.online_str() if self.live() else self.offline_str()


@dataclass
class Game:
    id: str
    name: str
    box_art_url: str
    markup: bool = True
    igdb_id: str | None = None

    @property
    def name_str(self) -> str:
        name = format.sanitize(self.name)
        return PangoSpan(name, weight='bold', size='medium', markup=self.markup)

    def __str__(self) -> str:
        return f'{self.name_str}'
