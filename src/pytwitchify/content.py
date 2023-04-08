# pytwitchify.content.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Optional

from pyselector.markup import PangoSpan

from pytwitchify import helpers


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
    vod_offset: Optional[int]
    markup: bool = True

    @property
    def name(self) -> str:
        return self.broadcaster_name

    @property
    def title_str(self) -> str:
        max_len = 65
        title = self.title[: max_len - 3] + "..." if len(self.title) > max_len else self.title
        if self.markup:
            title = helpers.remove_punctuation_escape_ampersand(title)
        return PangoSpan(title, size="large", foreground="silver") if self.markup else title

    @property
    def viewers(self) -> str:
        viewers = f"views: {helpers.format_number(self.view_count)}"
        return PangoSpan(viewers, size="medium", weight="light") if self.markup else viewers

    @property
    def duration_fmt(self) -> str:
        duration = f"duration: {self.duration}s"
        return PangoSpan(duration, size="medium", weight="light") if self.markup else duration

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def created_by(self) -> str:
        creator = f" [{self.creator_name}] "
        return (
            PangoSpan(creator, size="medium", weight="light", foreground="grey", style="italic")
            if self.markup
            else creator
        )

    def __str__(self) -> str:
        return f"{self.title_str}{self.created_by}{self.created_date} ({self.duration_fmt} | {self.viewers})"

    @property
    def created_date(self) -> str:
        created = helpers.format_datetime(self.created_at)
        return PangoSpan(created, size="x-large", foreground="orange", sub=True) if self.markup else created

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        return self.__str__()


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

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def title_str(self) -> str:
        max_len = 65
        title = self.title[: max_len - 3] + "..." if len(self.title) > max_len else self.title
        if self.markup:
            title = helpers.remove_punctuation_escape_ampersand(title)
        return PangoSpan(title, size="large", foreground="silver") if self.markup else title

    @property
    def viewers(self) -> str:
        viewers = helpers.format_number(self.view_count)
        return PangoSpan(viewers, size="medium", weight="light") if self.markup else viewers

    @property
    def duration_fmt(self) -> str:
        return PangoSpan(self.duration, size="medium", weight="light") if self.markup else self.duration

    def data(self) -> str:
        info = f" (duration: {self.duration_fmt} | views: {self.viewers}) "
        return PangoSpan(info, size="medium", weight="light", foreground="grey") if self.markup else info

    def __str__(self) -> str:
        return f"{self.title_str} {self.created_time}{self.data()}"

    @property
    def created_time(self) -> str:
        created = helpers.format_datetime(self.created_at)
        return PangoSpan(created, size="x-large", foreground="orange", sub=True) if self.markup else created

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        return self.__str__()


@dataclass
class Game:
    pass
