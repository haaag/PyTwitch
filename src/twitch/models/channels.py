from __future__ import annotations

from pydantic.dataclasses import dataclass
from pyselector.colors import Color
from pyselector.markup import PangoSpan
from twitch import format
from twitch.constants import LIVE_ICON
from twitch.constants import SEPARATOR
from twitch.constants import TWITCH_API_BASE_URL
from twitch.constants import TWITCH_CHAT_BASE_URL
from twitch.constants import TWITCH_STREAM_BASE_URL


@dataclass
class FollowedChannelInfo:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    tags: list[str] | None
    game_id: str
    game_name: str
    title: str
    delay: int
    content_classification_labels: list[str] | None = None
    is_branded_content: bool = False
    viewer_count: int = 0
    live: bool = False
    markup: bool = True
    playable: bool = False
    ansi: bool = False

    @property
    def name(self) -> str:
        return self.broadcaster_name

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight='bold', size='large', markup=self.markup)
        offline = PangoSpan(
            'Offline',
            foreground=Color.grey(),
            fg_ansi='grey',
            size='x-large',
            sub=True,
            alpha='45%',
            markup=self.markup,
            ansi=self.ansi,
        )
        return f'{user}{self.sep}{self.offline_icon} {offline}'

    @property
    def url(self) -> str:
        return str(TWITCH_API_BASE_URL.join(self.broadcaster_name))

    @property
    def category(self) -> str:
        game = format.sanitize(self.game_name)
        return PangoSpan(game, size='large', markup=self.markup)

    @property
    def offline_icon(self) -> str:
        return PangoSpan(
            LIVE_ICON,
            foreground=Color.grey(),
            fg_ansi='grey',
            size='large',
            alpha='50%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f'{self.broadcaster_login}/chat'))


@dataclass
class FollowedChannel:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    followed_at: str
    viewer_count: int = 0
    live: bool = False
    markup: bool = True
    playable: bool = False
    ansi: bool = False

    def __hash__(self):
        return hash((self.user_id, self.name))

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def name(self) -> str:
        return self.__str__()

    @property
    def offline_icon(self) -> str:
        return PangoSpan(
            LIVE_ICON,
            foreground=Color.grey(),
            fg_ansi='grey',
            size='large',
            alpha='50%',
            markup=self.markup,
            ansi=self.ansi,
        )

    def __str__(self) -> str:
        return self.broadcaster_name

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.broadcaster_name))

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f'{self.broadcaster_login}/chat'))


@dataclass
class Channel:
    broadcaster_language: str
    broadcaster_login: str
    display_name: str
    game_id: str
    game_name: str
    id: str
    is_live: bool
    started_at: str
    tag_ids: list[str]
    tags: list[str]
    thumbnail_url: str
    title: str
    markup: bool = True
    ansi: bool = False

    @property
    def user_id(self) -> str:
        return self.id

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def playable(self) -> bool:
        return self.is_live

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    @property
    def offline_icon(self) -> str:
        return PangoSpan(
            LIVE_ICON,
            foreground=Color.grey(),
            fg_ansi='grey',
            size='large',
            alpha='50%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def offline_str(self) -> str:
        return PangoSpan(
            'offline',
            foreground=Color.grey(),
            fg_ansi='grey',
            size='x-large',
            sub=True,
            alpha='45%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def online_icon(self) -> str:
        return PangoSpan(
            LIVE_ICON,
            foreground=Color.red(),
            fg_ansi='red',
            size='large',
            alpha='100%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def online_str(self) -> str:
        return PangoSpan(
            'online',
            foreground=Color.red(),
            fg_ansi='red',
            size='x-large',
            sub=True,
            alpha='100%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def icon(self) -> str:
        return self.online_icon if self.is_live else self.offline_icon

    @property
    def status(self) -> str:
        return self.online_str if self.is_live else self.offline_str

    def category(self) -> str:
        foreground = Color.yellow() if self.is_live else Color.grey()
        fg_ansi = 'yellow' if self.is_live else 'white'
        game = format.sanitize(self.game_name)
        return PangoSpan(
            game,
            foreground=foreground,
            fg_ansi=fg_ansi,
            size='x-large',
            sub=True,
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.broadcaster_login))

    def __str__(self) -> str:
        name = PangoSpan(
            self.display_name,
            fg_ansi='green' if self.is_live else 'white',
            weight='bold',
            size='large',
            markup=self.markup,
            ansi=self.ansi,
        )
        return f'{name}{self.sep}{self.icon} {self.status}{self.sep}{self.category()}'


@dataclass
class ChannelInfo:
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    followed_at: str
    live: bool = False
    markup: bool = True
    playable: bool = False
    ansi: bool = False

    def __hash__(self):
        return hash((self.user_id, self.name))

    @property
    def name(self) -> str:
        return self.broadcaster_name

    @property
    def icon_off(self) -> PangoSpan:
        return PangoSpan(
            LIVE_ICON,
            foreground='grey',
            fg_ansi='grey',
            size='small',
            alpha='50%',
            markup=self.markup,
            ansi=self.ansi,
        )

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha='100%', markup=self.markup)

    @property
    def offline(self) -> str:
        return PangoSpan(
            'offline',
            font_variant='small-caps',
            weight='bold',
            foreground='grey',
            fg_ansi='grey',
            size='medium',
            alpha='85%',
            markup=self.markup,
            ansi=self.ansi,
        )

    def __str__(self) -> str:
        user = PangoSpan(
            self.name,
            weight='bold',
            fg_ansi='white',
            size='large',
            markup=self.markup,
            ansi=self.ansi,
        )
        return f'{user}{self.sep}{self.icon_off} {self.offline}'
