# twitch.py

from __future__ import annotations

import logging
import typing
from collections import defaultdict
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional

from pytwitchify import api, helpers
from pytwitchify.follows import Category

if typing.TYPE_CHECKING:
    from pytwitchify.content import FollowedContentClip
    from pytwitchify.content import FollowedContentVideo
    from pytwitchify.datatypes import TwitchChannel
    from pytwitchify.datatypes import TwitchContent
    from pytwitchify.follows import FollowedChannel
    from pytwitchify.follows import FollowedChannelInfo

log = logging.getLogger(__name__)


class TwitchClient:
    def __init__(self, markup: bool = True) -> None:
        self.channels = api.ChannelsAPI()
        self._follows: Optional[Iterable[FollowedChannel]] = None
        self._follows_dict: Optional[dict[str, FollowedChannel]] = None
        self.markup = markup

    @property
    def get_channels(self) -> Iterable[FollowedChannel]:
        if not self._follows:
            self._follows = self.channels.channels
            return self._follows
        return self._follows

    @property
    def follows_dict(self) -> dict[str, FollowedChannel]:
        if not self._follows_dict:
            self._follows_dict = {f.name: f for f in self.get_channels}
        return self._follows_dict

    def follows_merged(self) -> Mapping[str, TwitchChannel]:
        """
        Merge followed channels with the list of currently live channels.

        Returns:
            A mapping of channel names to TwitchChannel objects.
        """
        online = {}
        follows = self.follows_dict

        for live in self.channels.get_channels_live:
            follows.pop(live.name, None)
            online[live.name] = live

        return {**online, **follows}

    def pavel_ameo(self) -> Mapping[str, TwitchChannel]:
        online: dict[str, TwitchChannel] = {}
        all_follows = {f.name: f for f in self.follows_info()}

        for live in self.channels.get_channels_live:
            all_follows.pop(live.name, None)
            online[live.name] = live

        return {**online, **all_follows}

    def follows_categorized(self) -> defaultdict[str, list[dict[str, FollowedChannelInfo]]]:
        categories = defaultdict(list)
        for b in self.follows_info():
            if b.name and b.game_name:
                categories[b.game_name].append({b.name: b})
        return categories

    def group_channels_by_game(self):
        # create a dictionary to group channels by game name
        channels_by_game = {}
        for _, channel in self.pavel_ameo().items():
            channel.markup = False
            if channel.category not in channels_by_game and channel.category != "":
                channels_by_game[channel.category] = []
            channels_by_game[channel.category].append(channel)

        # return the grouped channels as a dictionary
        return channels_by_game

    def group_channels_by_game_beta(self):
        channels_by_game = defaultdict(list)
        for _, channel in self.pavel_ameo().items():
            if channel.category != "" and channel.game_id != "":
                channel.markup = self.markup
                channels_by_game[helpers.clean_string(channel.game_name)].append(channel)
        return channels_by_game

    def follows_categorized_beta(self) -> Iterable[Category]:
        categories = self.group_channels_by_game_beta().items()
        return (Category(name=k, channels=v) for k, v in categories)

    def get_follows_ids(self) -> list[str]:
        return [follow.user_id for follow in self.get_channels]

    def follows_info(self) -> list[FollowedChannelInfo]:
        follows_id = [follow.user_id for follow in self.get_channels]
        return self.channels.get_channels_info(follows_id)

    def get_follow_by_name(self, follow: str) -> FollowedChannel:
        if not self.follows_dict.get(follow):
            raise KeyError(f"{follow=} not found")
        return self.follows_dict[follow]

    def get_follow_clips(self, follow_id: str) -> dict[str, FollowedContentClip]:
        clips = self.channels.content.get_clips(follow_id)
        return {f"{i}:::{clip.stringify(self.markup)}": clip for i, clip in enumerate(clips)}

    def get_follow_videos(self, follow_id: str) -> dict[str, FollowedContentVideo]:
        videos = self.channels.content.get_videos(follow_id)
        return {f"{i}:::{video.stringify(self.markup)}": video for i, video in enumerate(videos)}

    def get_follow_content(self, follow_id: str, content_type: str) -> Mapping[str, TwitchContent]:
        if content_type == "clips":
            content: Iterator[TwitchContent] = self.channels.content.get_clips(follow_id)
        elif content_type == "videos":
            content = self.channels.content.get_videos(follow_id)
        else:
            raise ValueError("Invalid content type specified.")

        return {f"{i}:::{item.stringify(self.markup)}": item for i, item in enumerate(content)}
