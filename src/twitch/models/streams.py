# streams.py

from __future__ import annotations

from pydantic.dataclasses import dataclass
from pyselector.colors import Color
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import LIVE_ICON
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
    tag_ids: list[str] | None
    tags: list[str] | None
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
    ansi: bool = False

    def __hash__(self):
        return hash((self.id, self.name))

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def title_str(self) -> str:
        title = format.sanitize(format.short(self.title, TITLE_MAX_LENGTH))
        return PangoSpan(title, size='medium', foreground='grey', fg_ansi='white', markup=self.markup, ansi=self.ansi)

    @property
    def live_since(self) -> str:
        since = format.calculate_live_time(self.started_at)
        return PangoSpan(
            f'({since})',
            sub=True,
            foreground=Color.grey(),
            fg_ansi='grey',
            size='x-large',
            style='italic',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def live_icon(self) -> str:
        return PangoSpan(
            LIVE_ICON,
            foreground=Color.red(),
            fg_ansi='red',
            size='large',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def viewers_fmt(self) -> str:
        viewers = format.number(self.viewer_count)
        return PangoSpan(
            viewers,
            size='medium',
            weight='bold',
            foreground=Color.red(),
            fg_ansi='red',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.user_login))

    @property
    def category(self) -> str:
        game = format.sanitize(self.game_name) if self.markup else self.game_name
        return PangoSpan(
            game,
            foreground='orange',
            fg_ansi='yellow',
            weight='bold',
            size='medium',
            font_variant='all-small-caps',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f'{self.user_login}/chat'))

    def __str__(self) -> str:
        user = PangoSpan(
            self.name,
            weight='bold',
            foreground=Color.cyan(),
            fg_ansi='cyan',
            size='large',
            markup=self.markup,
            ansi=self.ansi,
        )
        output = f'{user} {self.live_icon} {self.viewers_fmt} '
        output += f'{self.title_str} {self.live_since} {self.category}'
        return output
