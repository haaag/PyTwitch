# types.py

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Union

from src.twitch.content import FollowedContentClip
from src.twitch.content import FollowedContentVideo
from src.twitch.follows import FollowedChannel
from src.twitch.follows import FollowedChannelInfo
from src.twitch.follows import FollowedStream

QueryParamTypes = MutableMapping[str, Any]

HeaderTypes = Mapping[str, Any]

TwitchApiResponse = Mapping[str, Any]

TwitchChannel = Union[FollowedChannel, FollowedStream, FollowedChannelInfo]

TwitchContent = Union[FollowedContentClip, FollowedContentVideo]