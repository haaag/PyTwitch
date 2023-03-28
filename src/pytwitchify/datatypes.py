# types.py

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import MutableMapping
from typing import NamedTuple
from typing import Optional
from typing import Text
from typing import Union

from .utils import helpers


class Unicodes:
    BACK: Text = "\u21B6"
    BULLET_ICON: Text = "\u2022"
    CALENDAR: Text = "\U0001F4C5"
    CIRCLE: Text = "\u25CF"
    CLOCK: Text = "\U0001F559"
    CROSS: Text = "\u2716"
    DELIMITER: Text = "\u2014"
    EXIT: Text = "\uf842"
    EYE: Text = "\U0001F441"
    HEART: Text = "\u2665"
    BELL: Text = "\uf0f3"
    UNBELL: Text = "\uf1f6"


class ExecutableNotFoundError(Exception):
    pass


class ValidationEnvError(Exception):
    pass


class TwitchChannelVideo(NamedTuple):
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

    @property
    def title_str(self) -> str:
        max_length = 80
        return self.title[: max_length - 3] + "..." if len(self.title) > max_length else self.title

    @property
    def viewers(self) -> str:
        return f"viewers: {Unicodes.EYE} {self.view_count:,d}"

    def __str__(self) -> str:
        delimiter = f" {Unicodes.DELIMITER} "
        return f"{self.title_str}{delimiter}(duration: {self.duration} | {self.viewers})"


class BroadcasterInfo(NamedTuple):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    tags: list[str]
    game_id: str
    game_name: str
    title: str
    delay: int


@dataclass
class TwitchStreamLive:
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

    def __str__(self):
        delimiter = f" {Unicodes.DELIMITER} "
        name = f"{Unicodes.CIRCLE} {self.user_name:<20}"
        return f"{name}{self.title_str:<50}({self.live_since}{delimiter}{self.viewers})"

    @property
    def title_str(self) -> str:
        max_length = 50
        return self.title[: max_length - 3] + "..." if len(self.title) > max_length else self.title

    @property
    def live_since(self) -> str:
        return helpers.calculate_live_time(self.started_at)

    @property
    def viewers(self) -> str:
        return f"viewers: {Unicodes.EYE} {self.viewer_count:,d}"


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


class TwitchSavedStream(NamedTuple):
    id: str
    game_id: str
    game_name: str
    started_at: str
    thumbnail_url: str
    title: str
    user_id: str
    user_login: str
    user_name: str


class TwitchChannel(NamedTuple):
    user_id: int
    user_login: str
    user_name: str
    game_id: int
    game_name: str
    title: str
    thumbnail_url: str


class ChannelUserFollows(NamedTuple):
    from_id: str
    from_login: str
    from_name: str
    to_id: str
    to_login: str
    to_name: str
    followed_at: str

    def __str__(self) -> str:
        return self.to_name


class TwitchUserInfo(NamedTuple):
    broadcaster_type: str
    created_at: str
    description: str
    display_name: str
    id: int
    login: str
    offline_image_url: str
    profile_image_url: str
    type: str
    view_count: int


class TwitchClip(NamedTuple):
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

    @property
    def title_str(self) -> str:
        max_length = 40
        return self.title[: max_length - 3] + "..." if len(self.title) > max_length else self.title

    @property
    def creator_str(self) -> str:
        return f"creator: {self.creator_name}"

    @property
    def viewers(self) -> str:
        return f"viewers: {Unicodes.EYE} {self.view_count:,d}"

    def __str__(self) -> str:
        delimiter = f" {Unicodes.DELIMITER} "
        return f"{self.title_str}{delimiter}({self.creator_str}{delimiter}duration: {self.duration}'{delimiter}{self.viewers})"


QueryParamTypes = MutableMapping[str, Any]

HeaderTypes = Mapping[str, Any]

TwitchStreams = Iterable[TwitchStreamLive]

TwitchClips = Union[Iterator[TwitchClip], list[TwitchClip]]

TwitchApiResponse = Mapping[str, Any]

RequestData = Iterable[Any]

TwitchChannelSchedule = TwitchApiResponse

MenuOptions = Mapping[str, Callable[..., Optional[str]]]
