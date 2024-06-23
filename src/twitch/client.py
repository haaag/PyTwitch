# twitch.py

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Iterable

from twitch import format
from twitch.helpers import logme
from twitch.helpers import timeit
from twitch.models.category import Category
from twitch.models.category import Game
from twitch.models.channels import Channel
from twitch.models.channels import FollowedChannel
from twitch.models.channels import FollowedChannelInfo
from twitch.models.content import FollowedContentClip
from twitch.models.content import FollowedContentVideo
from twitch.models.streams import FollowedStream

if TYPE_CHECKING:
    from twitch.api import TwitchApi

logger = logging.getLogger(__name__)


def group_channels_by_game(
    channels: dict[str, FollowedChannelInfo | FollowedStream],
) -> dict[str, dict[str, FollowedChannelInfo | FollowedStream]]:
    output: dict[str, dict[str, FollowedChannelInfo | FollowedStream]] = {}
    for channel_name, channel in channels.items():
        if not channel.game_name:
            continue
        game_name = format.sanitize(channel.game_name)
        if game_name not in output:
            output[game_name] = {}
        output[game_name][channel_name] = channel
    return output


@logme('merging channels and streams')
def merge_data(
    channels: dict[str, FollowedChannelInfo],
    streams: dict[str, FollowedStream],
) -> dict[str, FollowedChannelInfo | FollowedStream]:
    """Merge followed channels with the list of currently live channels."""
    online = {}
    for live in streams.values():
        channels.pop(live.name, None)
        online[live.name] = live
    return {**online, **channels}


class TwitchClient:
    def __init__(self, api: TwitchApi, markup: bool = True) -> None:
        self.api = api
        self.markup = markup
        self._channels: dict[str, FollowedChannelInfo] | None = None
        self._streams: dict[str, FollowedStream] | None = None
        self._games: dict[str, Category] | None = None
        self._channels_and_streams: dict[str, FollowedChannelInfo | FollowedStream] = {}
        self.online: int = 0

    @property
    def channels(self) -> dict[str, FollowedChannelInfo]:
        if not self._channels:
            self._channels = {c.name: c for c in self.get_channels_with_info()}
        return self._channels

    @property
    def streams(self) -> dict[str, FollowedStream]:
        if not self._streams:
            self._streams = {s.name: s for s in self.get_streams()}
            self.online = len(self._streams)
        return self._streams

    @property
    def games(self) -> dict[str, Category]:
        if not self._games:
            self._games = {g.name: g for g in self.channels_categorized()}
        return self._games

    @property
    @timeit
    def channels_and_streams(self) -> dict[str, FollowedChannelInfo | FollowedStream]:
        if not self._channels_and_streams:
            logger.info('calling api for channels')
            channels = self.channels
            streams = self.streams
            self._channels_and_streams = merge_data(channels, streams)
        return self._channels_and_streams

    def get_streams(self) -> Iterable[FollowedStream]:
        streams = self.api.channels.get_streams()
        logger.info(f'{self.get_streams.__name__}: got {len(streams)} streams online')
        return (FollowedStream(**stream, markup=self.markup) for stream in streams)

    @logme("getting all user's channels")
    def get_channels(self) -> Iterable[FollowedChannel]:
        channels = self.api.channels.get_channels()
        logger.info(f'{self.get_channels.__name__}: got {len(channels)} channels')
        return (FollowedChannel(**channel, markup=self.markup) for channel in channels)

    def get_channel_info(self, channel_id: str) -> FollowedChannelInfo:
        data = self.api.channels.get_channel_info(user_id=channel_id)
        if not data:
            err_msg = f'{channel_id=} not found'
            logger.error(err_msg)
            raise ValueError(err_msg)
        return FollowedChannelInfo(**data[0], markup=self.markup)

    def get_channels_info(self, channels_id: list[str]) -> Iterable[FollowedChannelInfo]:
        data = self.api.channels.get_channels_info(broadcaster_ids=channels_id)
        if not data:
            err_msg = f'{channels_id=} not found'
            logger.error(err_msg)
            raise ValueError(err_msg)
        return (FollowedChannelInfo(**broadcaster, markup=self.markup) for broadcaster in data)

    def get_channels_with_info(self) -> Iterable[FollowedChannelInfo]:
        channels_id = [channel.user_id for channel in self.get_channels()]
        return self.get_channels_info(channels_id)

    @logme('getting channels by category')
    def channels_categorized(self) -> Iterable[Category]:
        channels_by_game = group_channels_by_game(self.channels_and_streams)
        return (Category(name=k, channels=channels_by_game[k], markup=self.markup) for k in channels_by_game)

    def get_channel_videos(self, user_id: str) -> Iterable[FollowedContentVideo]:
        data = self.api.content.get_videos(user_id=user_id)
        return (FollowedContentVideo(**video, markup=self.markup) for video in data)

    def get_channel_clips(self, user_id: str) -> Iterable[FollowedContentClip]:
        data = self.api.content.get_clips(user_id=user_id)
        return (FollowedContentClip(**clip, markup=self.markup) for clip in data)

    def get_streams_by_game_id(self, game_id: str) -> Iterable[FollowedStream]:
        logger.debug('getting streams by game_id: %s', game_id)
        data = self.api.content.get_streams_by_game_id(game_id)
        return (FollowedStream(**item, markup=self.markup) for item in data)

    def get_games_by_query(self, query: str) -> Iterable[Game]:
        data = self.api.content.search_categories(query)
        return (Game(**item, markup=self.markup) for item in data)

    def get_channels_by_query(self, query: str, live_only: bool = True) -> Iterable[FollowedChannel]:
        data = self.api.content.search_channels(query, live_only=live_only)
        return (Channel(**item, markup=self.markup) for item in data if item['game_name'])

    @logme('getting top streams')
    def get_top_streams(self) -> Iterable[FollowedStream]:
        data = self.api.content.get_top_streams()
        return (FollowedStream(**s, markup=self.markup) for s in data)
