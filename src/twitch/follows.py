# twitch.follows

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from pyselector.markup import PangoSpan

from src.twitch import helpers
from src.twitch.constants import LIVE_ICON
from src.twitch.constants import LIVE_ICON_COLOR
from src.twitch.constants import SEPARATOR
from src.twitch.constants import TITLE_MAX_LENGTH
from src.twitch.constants import TWITCH_API_BASE_URL
from src.twitch.constants import TWITCH_CHAT_BASE_URL
from src.twitch.constants import TWITCH_STREAM_BASE_URL


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
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%") if self.markup else SEPARATOR

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight="bold", size="large") if self.markup else self.name
        offline = (
            PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%") if self.markup else "Offline"
        )
        return f"{user}{self.sep}{self.offline_icon} {offline}"

    @property
    def url(self) -> str:
        return str(TWITCH_API_BASE_URL.join(self.broadcaster_name))

    @property
    def category(self) -> str:
        return PangoSpan(helpers.clean_string(self.game_name), size="large") if self.markup else self.game_name

    @property
    def offline_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground="grey", size="large", alpha="50%") if self.markup else LIVE_ICON

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

    def __hash__(self):
        return hash((self.id, self.name))

    @property
    def name(self) -> str:
        return self.user_name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%") if self.markup else SEPARATOR

    def __str__(self) -> str:
        user = PangoSpan(self.name, weight="bold", size="large") if self.markup else self.name
        return f"{user}{self.sep}{self.live_icon} {self.viewers_fmt} {self.title_str} {self.live_since} {self.category}"

    @property
    def title_str(self) -> str:
        title = self.title[: TITLE_MAX_LENGTH - 3] + "..." if len(self.title) > TITLE_MAX_LENGTH else self.title
        if self.markup:
            title = helpers.clean_string(title)
        return PangoSpan(title, size="large", foreground="grey") if self.markup else title

    @property
    def live_since(self) -> str:
        since = helpers.calculate_live_time(self.started_at)
        # since = self.started_at
        return PangoSpan(f"({since})", sub=True, size="x-large", style="italic") if self.markup else f"({since})"

    @property
    def live_icon(self) -> str:
        return PangoSpan(LIVE_ICON, foreground=LIVE_ICON_COLOR, size="large") if self.markup else LIVE_ICON

    @property
    def viewers_fmt(self) -> str:
        viewers = helpers.format_number(self.viewer_count)
        return PangoSpan(viewers, size="small", weight="bold", foreground=LIVE_ICON_COLOR) if self.markup else viewers

    @property
    def url(self) -> str:
        return str(TWITCH_STREAM_BASE_URL.join(self.user_name))

    @property
    def category(self) -> str:
        game = helpers.clean_string(self.game_name)
        return PangoSpan(game, foreground="orange", size="x-large", sub=True) if self.markup else self.game_name

    @property
    def chat(self) -> str:
        return str(TWITCH_CHAT_BASE_URL.join(f"{self.user_login}/chat"))


@dataclass
class Category:
    name: str
    channels: dict[str, Union[FollowedStream, FollowedChannelInfo]]
    markup: bool = True

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
        return PangoSpan(viewers, size="small", weight="bold", foreground="grey") if self.markup else viewers

    @property
    def online_str(self) -> str:
        if self.online == 0:
            return ""
        live = f"{LIVE_ICON} {self.online}"
        return PangoSpan(live, foreground=LIVE_ICON_COLOR, size="medium", weight="bold") if self.markup else live

    @property
    def name_str(self) -> str:
        return PangoSpan(self.name, weight="bold", size="large") if self.markup else self.name

    @property
    def sep(self) -> str:
        return PangoSpan(SEPARATOR, alpha="100%") if self.markup else SEPARATOR

    def __str__(self) -> str:
        offline = (
            PangoSpan("Offline", foreground="grey", size="x-large", sub=True, alpha="45%") if self.markup else "Offline"
        )
        return (
            f"{self.name_str}{self.sep}{self.online_str} {self.viewers_fmt}"
            if self.online
            else f"{self.name_str}{self.sep}{LIVE_ICON} {offline}"
        )


game_from_search = {
    "broadcaster_language": "en",
    "broadcaster_login": "12g_live",
    "display_name": "12G_Live",
    "game_id": "504461",
    "game_name": "Super Smash Bros. Ultimate",
    "id": "866258853",
    "is_live": True,
    "tag_ids": [],
    "tags": [
        "Shooter",
        "teamplay",
        "Tournament",
        "Smashbrosultimate",
        "Bracket",
        "NewYork",
        "BrookLAN",
        "12G",
        "FightingsGames",
        "English",
    ],
    "thumbnail_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/11c7516e-88bd-46f2-bbfc-428db7e467f8-profile_image-300x300.png",
    "title": "BrookLAN Brawls #73 ft.  Ho3K | John Numbers, WPC | Vivi, Sho, Kamex, 5teelix and the 12G crew! $200 pot bonus for Gen beating Riddles!",
    "started_at": "2023-04-23T19:29:28Z",
}
