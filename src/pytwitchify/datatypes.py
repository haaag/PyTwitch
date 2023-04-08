# types.py

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Union

from pytwitchify.content import FollowedContentClip
from pytwitchify.content import FollowedContentVideo
from pytwitchify.follows import FollowedChannel
from pytwitchify.follows import FollowedChannelInfo
from pytwitchify.follows import FollowedChannelLive

QueryParamTypes = MutableMapping[str, Any]

HeaderTypes = Mapping[str, Any]

TwitchApiResponse = Mapping[str, Any]

TwitchChannel = Union[FollowedChannel, FollowedChannelLive, FollowedChannelInfo]

TwitchContent = Union[FollowedContentClip, FollowedContentVideo]

TwitchPlayableContent = Union[FollowedChannelLive, TwitchContent]

FollowsByCategory = dict[str, list[dict[str, Union[FollowedChannelInfo, int]]]]
