# fetcher.py

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Protocol

from twitch.helpers import logme
from twitch.models.category import Category
from twitch.models.category import Game
from twitch.models.channels import Channel
from twitch.models.channels import ChannelInfo
from twitch.models.channels import FollowedChannel
from twitch.models.content import FollowedContentClip
from twitch.models.content import FollowedContentVideo
from twitch.models.streams import FollowedStream

if TYPE_CHECKING:
    from twitch.api import TwitchApi

logger = logging.getLogger(__name__)


class Item(Protocol):
    name: str
    live: bool
    game_name: str


def create_categories(streams_data: list[list[dict[str, Any]]], markup: bool) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for cat_data in streams_data:
        cat_name = cat_data[0]['game_name']
        streams = (FollowedStream(**c, markup=markup) for c in cat_data)
        all_streams = {s.name: s for s in streams}
        category = Category(name=cat_name, channels=all_streams, markup=markup)
        viewers = category.total_viewers_fmt()
        logger.info(f"game '{cat_name}' has {category.channels_live()} streams with {viewers} viewers")
        categories[cat_name] = category
    return categories


@logme('merging channels offline and streams')
def merge_data(channels: dict[str, Item], streams: dict[str, Item]) -> dict[str, Item]:
    """Merge followed channels with the list of currently live channels."""
    return {**streams, **{k: v for k, v in channels.items() if k not in streams}}


class TwitchFetcher:
    def __init__(self, api: TwitchApi, markup: bool = True) -> None:
        self.api = api
        self.markup = markup
        self.online: int = 0

    async def close(self) -> None:
        return await self.api.close()

    async def channels_and_streams(self) -> dict[str, Item]:
        cdata, sdata = await asyncio.gather(
            self.api.channels.all(),
            self.api.channels.streams(),
        )

        m = self.markup
        c = {c['broadcaster_name']: ChannelInfo(**c, markup=m) for c in cdata if 'type' not in c}
        s = {s['user_name']: FollowedStream(**s, markup=m) for s in sdata if 'type' in s}
        self.online = len(s)
        return merge_data(c, s)

    async def videos(self, user_id: str) -> Iterable[FollowedContentVideo]:
        data = await self.api.content.get_videos(user_id=user_id)
        return (FollowedContentVideo(**video, markup=self.markup) for video in data)

    async def clips(self, user_id: str) -> Iterable[FollowedContentClip]:
        data = await self.api.content.get_clips(user_id=user_id)
        return (FollowedContentClip(**clip, markup=self.markup) for clip in data)

    async def streams_by_game_id(self, game_id: str) -> Iterable[FollowedStream]:
        logger.debug('getting streams by game_id: %s', game_id)
        data = await self.api.content.get_streams_by_game_id(game_id)
        return (FollowedStream(**item, markup=self.markup) for item in data)

    async def games_by_query(self, query: str) -> Iterable[Game]:
        data = await self.api.content.search_categories(query)
        return (Game(**item, markup=self.markup) for item in data)

    async def channels_by_query(self, query: str, live_only: bool = True) -> Iterable[FollowedChannel]:
        data = await self.api.content.search_channels(query, live_only=live_only)
        data_sorted_by_live = sorted(data, key=lambda c: c['is_live'], reverse=True)
        return (Channel(**item, markup=self.markup) for item in data_sorted_by_live if item['game_name'])

    async def top_streams(self) -> Iterable[FollowedStream]:
        data = await self.api.content.get_top_streams()
        return (FollowedStream(**s, markup=self.markup) for s in data)

    async def top_games(self) -> Iterable[Category]:
        data = await self.api.content.get_top_games()
        return (Game(**g, markup=self.markup) for g in data)

    async def top_games_with_streams(self) -> dict[str, Category]:
        max_games = 25
        max_streams = 25
        top_games = await self.top_games()
        games_streams_data = await self._top_games_streams_data(top_games, max_games, max_streams)
        return create_categories(games_streams_data, self.markup)

    async def _top_games_streams_data(
        self, top_games: Iterable[Category], max_games: int, max_streams: int
    ) -> list[list[dict[str, Any]]]:
        task: list[asyncio.Task] = []
        create = asyncio.create_task
        for game in top_games:
            if len(task) == max_games:
                break
            task.append(create(self.api.content.get_streams_by_game_id(game.id, max_items=max_streams)))
        return await asyncio.gather(*task)
