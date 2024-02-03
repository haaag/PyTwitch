# twitch.content.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
    markup: bool = True
    playable: bool = True

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
        return PangoSpan(SEPARATOR, alpha='100%') if self.markup else SEPARATOR

    @property
    def title_str(self) -> str:
        title = self.title[: TITLE_MAX_LENGTH - 3] + '...' if len(self.title) > TITLE_MAX_LENGTH else f'{self.title} '
        if self.markup:
            title = format.sanitize(title)
        return PangoSpan(title, size='large', foreground='silver') if self.markup else title

    @property
    def viewers_fmt(self) -> str:
        viewers = f'views: {format.number(self.view_count)}'
        return PangoSpan(viewers, size='medium', weight='light') if self.markup else viewers

    @property
    def duration_fmt(self) -> str:
        duration = f'duration: {self.duration}s'
        return PangoSpan(duration, size='medium', weight='light') if self.markup else duration

    @property
    def item_id(self) -> str:
        return PangoSpan(self.key, foreground='grey') if self.markup else self.key

    @property
    def created_date(self) -> str:
        created = format.date(self.created_at)
        return PangoSpan(created, size='large', foreground='orange', sub=True) if self.markup else created

    def __str__(self) -> str:
        return f'{self.item_id}{self.sep}{self.created_date} {self.title_str} ({self.duration_fmt}{self.sep}{self.viewers_fmt})'  # noqa: E501


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

    @property
    def key(self) -> str:
        return self.stream_id

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%') if self.markup else SEPARATOR

    @property
    def title_str(self) -> str:
        title = self.title[: TITLE_MAX_LENGTH - 3] + '...' if len(self.title) > TITLE_MAX_LENGTH else f'{self.title} '
        if self.markup:
            title = format.sanitize(title)
        return PangoSpan(title, size='large', foreground='silver') if self.markup else title

    @property
    def viewers_fmt(self) -> str:
        viewers = format.number(self.view_count)
        return PangoSpan(viewers, size='medium', weight='light') if self.markup else viewers

    @property
    def duration_fmt(self) -> str:
        return PangoSpan(self.duration, size='medium', weight='light') if self.markup else self.duration

    @property
    def video_str(self) -> str:
        return PangoSpan(self.key, size='small', foreground='grey') if self.markup else self.key

    @property
    def created_date(self) -> str:
        created = format.date(self.created_at)
        return PangoSpan(created, size='x-large', foreground='orange', sub=True) if self.markup else created

    @property
    def published_fmt(self) -> str:
        return format.date(self.published_at)

    def __str__(self) -> str:
        return (
            f'{self.video_str}{self.sep}{self.title_str} {self.created_date} ({self.duration_fmt} | {self.viewers_fmt})'
        )
