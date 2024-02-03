# twitch.follows

from __future__ import annotations

from dataclasses import dataclass

from twitch import helpers
from twitch.constants import LIVE_ICON
from twitch.constants import LIVE_ICON_COLOR
from twitch.constants import SEPARATOR
from twitch.constants import TITLE_MAX_LENGTH
from twitch.constants import TWITCH_API_BASE_URL
from twitch.constants import TWITCH_CHAT_BASE_URL
from twitch.constants import TWITCH_STREAM_BASE_URL
from twitch.markup import PangoSpan


@dataclass
class FollowedChannelInfo:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    tags: list[str]
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

    @property
    def name(self) -> str:
        return self.broadcaster_name

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%", markup=self.markup)

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight="bold", size="large", markup=self.markup)
        offline = PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%", markup=self.markup)
        return f"{user}{self.sep}{self.offline_icon} {offline}"

    @property
    def url(self) -> str:
        return str(TWITCH_API_BASE_URL.join(self.broadcaster_name))

    @property
    def category(self) -> str:
        return PangoSpan(helpers.clean_string(self.game_name), size="large") if self.markup else self.game_name

    @property
    def offline_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground="grey", size="large", alpha="50%", markup=self.markup)

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f"{self.broadcaster_login}/chat"))


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
        return PangoSpan(LIVE_ICON, foreground="grey", size="large", alpha="50%") if self.markup else LIVE_ICON

    def __str__(self) -> str:
        return self.broadcaster_name

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.broadcaster_name))

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f"{self.broadcaster_login}/chat"))


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
        return PangoSpan(SEPARATOR, alpha="100%", markup=self.markup)

    @property
    def title_str(self) -> str:
        title = self.title[: TITLE_MAX_LENGTH - 3] + "..." if len(self.title) > TITLE_MAX_LENGTH else self.title
        if self.markup:
            title = helpers.clean_string(title)
        return PangoSpan(title, size="medium", foreground="grey", markup=self.markup)

    @property
    def live_since(self) -> str:
        since = helpers.calculate_live_time(self.started_at)
        return PangoSpan(f"({since})", sub=True, size="x-large", style="italic", markup=self.markup)

    @property
    def live_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground=LIVE_ICON_COLOR, size="large", markup=self.markup)

    @property
    def viewers_fmt(self) -> str:
        viewers = helpers.format_number(self.viewer_count)
        return PangoSpan(viewers, size="medium", weight="bold", foreground=LIVE_ICON_COLOR, markup=self.markup)

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.user_name))

    @property
    def category(self) -> str:
        game = helpers.clean_string(self.game_name) if self.markup else self.game_name
        return PangoSpan(game, foreground="orange", size="x-large", sub=True, markup=self.markup)

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f"{self.user_login}/chat"))

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight="bold", size="large", markup=self.markup)
        return f"{user}{self.sep}{self.live_icon} {self.viewers_fmt} {self.title_str} {self.live_since} {self.category}"


@dataclass
class Category:
    name: str
    channels: dict[str, FollowedStream | FollowedChannelInfo]
    markup: bool = True
    playable: bool = False

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def online(self) -> int:
        return sum(1 for c in self.channels.values() if c.live)

    @property
    def viewers_fmt(self) -> str:
        if self.online == 0:
            return ""
        viewers_str = helpers.format_number(sum(c.viewer_count for c in self.channels.values()))
        viewers = f"{viewers_str} viewers"
        return PangoSpan(viewers, size="small", weight="bold", foreground="grey", markup=self.markup)

    @property
    def online_str(self) -> str:
        if self.online == 0:
            return ""
        live = f"{LIVE_ICON} {self.online}"
        return PangoSpan(live, foreground=LIVE_ICON_COLOR, size="medium", weight="bold", markup=self.markup)

    @property
    def name_str(self) -> str:
        return PangoSpan(self.name, weight="bold", size="large", markup=self.markup)

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%", markup=self.markup)

    def __str__(self) -> str:
        offline = PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%", markup=self.markup)
        return (
            f"{self.name_str}{self.sep}{self.online_str} {self.viewers_fmt}"
            if self.online
            else f"{self.name_str}{self.sep}{LIVE_ICON} {offline}"
        )


@dataclass
class Game:
    id: str
    name: str
    box_art_url: str
    markup: bool = True

    @property
    def name_str(self) -> str:
        return PangoSpan(self.name, weight="bold", size="medium", markup=self.markup)

    def __str__(self) -> str:
        return f"{self.name_str}"


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

    @property
    def user_id(self) -> str:
        return self.id

    @property
    def name(self) -> str:
        return PangoSpan(self.display_name, weight="bold", size="large", markup=self.markup)

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%", markup=self.markup)

    @property
    def offline_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground="grey", size="large", alpha="50%", markup=self.markup)

    @property
    def offline_str(self) -> str:
        return PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%", markup=self.markup)

    @property
    def online_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground=LIVE_ICON_COLOR, size="large", alpha="100%", markup=self.markup)

    @property
    def online_str(self) -> str:
        return PangoSpan(
            "Online", foreground=LIVE_ICON_COLOR, size="x-large", sub=True, alpha="100%", markup=self.markup
        )

    @property
    def icon(self) -> str:
        return self.online_icon if self.is_live else self.offline_icon

    @property
    def status(self) -> str:
        return self.online_str if self.is_live else self.offline_str

    def category(self) -> str:
        color = "orange" if self.is_live else "grey"
        game = helpers.clean_string(self.game_name)
        return PangoSpan(game, foreground=color, size="x-large", sub=True, markup=self.markup)

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.broadcaster_login))

    def __str__(self) -> str:
        return f"{self.name}{self.sep}{self.icon} {self.status}{self.sep}{self.category()}"
