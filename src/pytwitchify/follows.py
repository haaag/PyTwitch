# pytwitchify.follows

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple
from typing import Union

from pyselector.markup import PangoSpan

from pytwitchify import helpers
from pytwitchify.constants import API_TWITCH_BASE_URL
from pytwitchify.constants import LIVE_ICON
from pytwitchify.constants import LIVE_ICON_COLOR
from pytwitchify.constants import STREAM_TWITCH_BASE_URL


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
    viewer_count: int = 0
    live: bool = False
    markup: bool = True

    @property
    def name(self) -> str:
        return self.broadcaster_name

    @property
    def user_id(self) -> str:
        return self.broadcaster_id

    @property
    def url(self) -> str:
        return str(API_TWITCH_BASE_URL.join(self.broadcaster_name))

    @property
    def category(self) -> str:
        return PangoSpan(helpers.clean_string(self.game_name), size="large") if self.markup else self.game_name

    @property
    def offline_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground="grey", size="large", alpha="50%") if self.markup else LIVE_ICON

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        username = f"{self.name} {self.offline_icon}"
        user = PangoSpan(username, weight="bold", size="large") if self.markup else username
        offline = PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%") if self.markup else ""
        return f"{user} {offline}"


@dataclass
class FollowedChannel:
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    followed_at: str
    viewer_count: int = 0
    live: bool = False
    markup: bool = True

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
        return str(STREAM_TWITCH_BASE_URL.join(self.broadcaster_name))

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        username = f"{self.name} {self.offline_icon}"
        user = PangoSpan(username, weight="bold", size="large", alpha="50%") if self.markup else username
        offline = PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%") if self.markup else ""
        return f"{user} {offline}"


@dataclass
class FollowedChannelLive:
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

    def __hash__(self):
        return hash((self.id, self.name))

    @property
    def name(self) -> str:
        return self.user_name

    def __str__(self) -> str:
        return self.user_name

    @property
    def title_str(self) -> str:
        max_len = 80
        title = self.title[: max_len - 3] + "..." if len(self.title) > max_len else self.title
        if self.markup:
            title = helpers.clean_string(title)
        return PangoSpan(title, size="medium", foreground="grey") if self.markup else title

    @property
    def live_since(self) -> str:
        since = helpers.calculate_live_time(self.started_at)
        return PangoSpan(f"({since})", sub=True, size="x-large", style="italic") if self.markup else f"({since})"

    @property
    def live_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground=LIVE_ICON_COLOR, size="large") if self.markup else LIVE_ICON

    @property
    def viewers(self) -> str:
        viewers = helpers.format_number(self.viewer_count)
        return PangoSpan(viewers, size="small", weight="bold", foreground=LIVE_ICON_COLOR) if self.markup else viewers

    @property
    def url(self) -> str:
        return str(STREAM_TWITCH_BASE_URL.join(self.user_name))

    @property
    def category(self) -> str:
        game = helpers.clean_string(self.game_name)
        return PangoSpan(game, foreground="orange", size="x-large", sub=True) if self.markup else self.game_name

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        user = PangoSpan(self.name, weight="bold", size="large") if self.markup else self.name
        return f"{user} {self.live_icon} {self.viewers} {self.title_str} {self.live_since} {self.category}"


@dataclass
class Category:
    name: str
    channels: list[Union[FollowedChannel, FollowedChannelLive, FollowedChannelInfo]]
    markup: bool = True

    @property
    def online(self) -> int:
        return sum(1 for c in self.channels if c.live)

    @property
    def length(self) -> int:
        return len(self.channels)

    @property
    def viewers(self) -> str:
        if self.online == 0:
            return ""
        viewers_fmt = helpers.format_number(sum(c.viewer_count for c in self.channels))
        viewers = f"({viewers_fmt} viewers)"
        return PangoSpan(viewers, size="small", weight="bold", foreground="grey") if self.markup else viewers

    @property
    def online_str(self) -> str:
        if self.online == 0:
            return ""
        live = f"channels {LIVE_ICON} {self.online}"
        return PangoSpan(live, foreground=LIVE_ICON_COLOR, size="small", weight="bold") if self.markup else live

    @property
    def name_str(self) -> str:
        return PangoSpan(self.name, weight="bold", size="large") if self.markup else self.name

    def __str__(self) -> str:
        return f"{self.name_str} {self.online_str} {self.viewers}" if self.viewers and self.markup else self.name

    def stringify(self, markup: bool = True) -> str:
        self.markup = markup
        return (
            PangoSpan(helpers.clean_string(self.name), foreground="grey", size="x-large", sub=True)
            if self.markup
            else self.name
        )


class SearchChannelsAPIResponse(NamedTuple):
    id: str
    game_id: str
    game_name: str
    broadcaster_language: str
    broadcaster_login: str
    display_name: str
    is_live: bool
    started_at: str
    tags: list[str]
    tag_ids: list[str]
    thumbnail_url: str
    title: str
