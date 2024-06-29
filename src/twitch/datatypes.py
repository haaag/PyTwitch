# types.py

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Union

from twitch.models.channels import ChannelInfo
from twitch.models.channels import FollowedChannel
from twitch.models.channels import FollowedChannelInfo
from twitch.models.content import FollowedContentClip
from twitch.models.content import FollowedContentVideo
from twitch.models.streams import FollowedStream

QueryParamTypes = MutableMapping[str, Any]

HeaderTypes = Mapping[str, Any]

TwitchApiResponse = Mapping[str, Any]

TwitchChannel = Union[
    FollowedChannel,
    FollowedStream,
    FollowedChannelInfo,
    ChannelInfo,
]

TwitchContent = Union[
    FollowedContentClip,
    FollowedContentVideo,
    TwitchChannel,
]
