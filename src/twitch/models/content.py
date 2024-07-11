# twitch.content.py

from __future__ import annotations

from typing import Any

from pydantic.dataclasses import dataclass
from pyselector.colors import Color
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import SEPARATOR
from twitch.constants import TITLE_MAX_LENGTH


@dataclass
class FollowedContentClip:
    broadcaster_id: str
    broadcaster_name: str
    created_at: str
    creator_id: str
    creator_name: str
    duration: float
    embed_url: str
    game_id: str
    id: str
    language: str
    thumbnail_url: str
    title: str
    url: str
    video_id: str
    view_count: int
    vod_offset: int | None
    is_featured: bool = False
    markup: bool = True
    playable: bool = True
    ansi: bool = False

    @property
    def key(self) -> str:
        return self.id[:10]

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def name(self) -> str:
        return self.creator_name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    @property
    def title_fmt(self) -> str:
        title = format.sanitize(format.short(self.title, TITLE_MAX_LENGTH))
        return PangoSpan(
            title,
            size='medium',
            foreground=Color.white(),
            fg_ansi='white',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def viewers_fmt(self) -> str:
        viewers = f'views: {format.number(self.view_count)}'
        return PangoSpan(
            viewers,
            size='medium',
            weight='light',
            foreground=Color.red(),
            fg_ansi='red',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def duration_fmt(self) -> str:
        duration = f'duration: {self.duration}s'
        return PangoSpan(
            duration,
            size='medium',
            weight='light',
            foreground='orange',
            fg_ansi='yellow',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def item_id(self) -> str:
        return PangoSpan(self.key, foreground=Color.grey(), fg_ansi='grey', markup=self.markup, ansi=self.ansi)

    @property
    def created_date(self) -> str:
        return PangoSpan(
            format.date(self.created_at),
            size='medium',
            foreground='orange',
            fg_ansi='yellow',
            weight='bold',
            font_variant='all-small-caps',
            markup=self.markup,
            ansi=self.ansi,
        )

    def __str__(self) -> str:
        id_and_date = f'{self.item_id}{self.sep}{self.created_date}'
        dur_and_viewers = f'{self.duration_fmt}{self.sep}{self.viewers_fmt}'
        return f'{id_and_date} {self.title_fmt} {dur_and_viewers}'


@dataclass
class FollowedContentVideo:
    user_id: str
    user_login: str
    user_name: str
    view_count: int
    viewable: str
    url: str
    type: str
    title: str
    thumbnail_url: str
    stream_id: str
    published_at: str
    muted_segments: Any
    language: str
    id: str
    duration: str
    description: str
    created_at: str
    markup: bool = True
    playable: bool = True
    ansi: bool = False

    @property
    def key(self) -> str:
        return self.stream_id[:4]

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    @property
    def title_fmt(self) -> str:
        title = format.sanitize(format.short(self.title, TITLE_MAX_LENGTH))
        return PangoSpan(
            title,
            size='medium',
            foreground=Color.white(),
            fg_ansi='white',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def viewers_fmt(self) -> str:
        viewers = format.number(self.view_count)
        return PangoSpan(
            viewers,
            size='medium',
            weight='light',
            foreground=Color.red(),
            fg_ansi='red',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def duration_fmt(self) -> str:
        return PangoSpan(
            self.duration,
            size='medium',
            weight='light',
            fg_ansi='yellow',
            foreground='orange',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def item_id(self) -> str:
        return PangoSpan(
            self.key,
            size='small',
            foreground='grey',
            fg_ansi='grey',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def created_at_fmt(self) -> str:
        return PangoSpan(
            format.date(self.created_at),
            size='medium',
            weight='bold',
            foreground='orange',
            fg_ansi='yellow',
            font_variant='all-small-caps',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def published_fmt(self) -> str:
        return format.date(self.published_at)

    def __str__(self) -> str:
        id_and_date = f'{self.item_id}{self.sep}{self.created_at_fmt}'
        return f'{id_and_date}{self.sep}{self.title_fmt} {self.duration_fmt}{self.sep}{self.viewers_fmt}'
