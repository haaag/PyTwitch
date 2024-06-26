# streams.py

from __future__ import annotations

from pydantic.dataclasses import dataclass
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import LIVE_ICON
from twitch.constants import LIVE_ICON_COLOR
from twitch.constants import SEPARATOR
from twitch.constants import TITLE_MAX_LENGTH
from twitch.constants import TWITCH_CHAT_BASE_URL
from twitch.constants import TWITCH_STREAM_BASE_URL


@dataclass
class FollowedStream:
    id: str
    game_id: str
    game_name: str
    is_mature: bool
    language: str
    started_at: str
    tag_ids: list[str]
    tags: list[str]
    thumbnail_url: str
    title: str
    type: str
    user_id: str
    user_login: str
    user_name: str
    viewer_count: int
    live: bool = True
    markup: bool = True
    playable: bool = True

    def __hash__(self):
        return hash((self.id, self.name))

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    @property
    def title_str(self) -> str:
        title = self.title[: TITLE_MAX_LENGTH - 3] + '...' if len(self.title) > TITLE_MAX_LENGTH else self.title
        if self.markup:
            title = format.sanitize(title)
        return PangoSpan(title, size='medium', foreground='grey', markup=self.markup)

    @property
    def live_since(self) -> str:
        since = format.calculate_live_time(self.started_at)
        return PangoSpan(f'({since})', sub=True, size='x-large', style='italic', markup=self.markup)

    @property
    def live_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground=LIVE_ICON_COLOR, size='large', markup=self.markup)

    @property
    def viewers_fmt(self) -> str:
        viewers = format.number(self.viewer_count)
        return PangoSpan(viewers, size='medium', weight='bold', foreground=LIVE_ICON_COLOR, markup=self.markup)

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.user_name))

    @property
    def category(self) -> str:
        game = format.sanitize(self.game_name) if self.markup else self.game_name
        return PangoSpan(game, foreground='orange', size='x-large', sub=True, markup=self.markup)

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f'{self.user_login}/chat'))

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight='bold', size='large', markup=self.markup)
        return f'{user}{self.sep}{self.live_icon} {self.viewers_fmt} {self.title_str} {self.live_since} {self.category}'
