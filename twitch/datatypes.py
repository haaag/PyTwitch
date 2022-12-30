# types.py

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Union


class ValidationEnvError(Exception):
    pass


@dataclass
class TwitchChannelVideo:
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


@dataclass
class BroadcasterInfo:
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


@dataclass
class SearchChannelsAPIResponse:
    id: str
    game_id: str
    game_name: str
    broadcaster_language: str
    broadcaster_login: str
    display_name: str
    is_live: bool
    started_at: str
    tag_ids: list[str]
    thumbnail_url: str
    title: str


@dataclass
class TwitchSavedStream:
    id: str
    game_id: str
    game_name: str
    started_at: str
    thumbnail_url: str
    title: str
    user_id: str
    user_login: str
    user_name: str


@dataclass
class TwitchChannel:
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


@dataclass
class TwitchUserInfo:
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


@dataclass
class TwitchClip:
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
    vod_offset: int


QueryParamTypes = Mapping[str, Any]

HeaderTypes = Mapping[str, Any]

TwitchStreams = Iterable[TwitchStreamLive]

TwitchClips = Union[Iterator[TwitchClip], list[TwitchClip]]

TwitchApiResponse = Mapping[str, Any]

RequestData = Iterable[Any]

TwitchChannelSchedule = TwitchApiResponse

MenuOptions = Mapping[str, Callable[..., Optional[str]]]
