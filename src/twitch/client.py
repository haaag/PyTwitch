# fetcher.py

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Protocol

from twitch.helpers import astimeit
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


def create_categories(streams_data: list[list[dict[str, Any]]], markup: bool, ansi: bool) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for cat_data in streams_data:
        if len(cat_data) == 0:
            continue
        cat_name = cat_data[0]['game_name']
        streams = (FollowedStream(**c, markup=markup, ansi=ansi) for c in cat_data)
        all_streams = {s.name: s for s in streams}
        category = Category(name=cat_name, channels=all_streams, markup=markup, ansi=ansi)
        viewers = category.total_viewers_fmt()
        logger.info(f"game '{cat_name}' has {category.channels_live()} streams with {viewers} viewers")
        categories[cat_name] = category
    categories_sorted = sorted(categories.items(), key=lambda x: x[1].total_viewers(), reverse=True)
    return dict(categories_sorted)


@logme('merging channels offline and streams')
def merge_data(channels: Mapping[str, Item], streams: Mapping[str, Item]) -> Mapping[str, Item]:
    """Merge followed channels with the list of currently live channels."""
    return {**streams, **{k: v for k, v in channels.items() if k not in streams}}


class TwitchFetcher:
    def __init__(self, api: TwitchApi) -> None:
        self.api = api
        self.online: int = 0

    async def close(self) -> None:
        return await self.api.close()

    @astimeit
    async def channels_and_streams(self, markup: bool, ansi: bool) -> Mapping[str, Item]:
        cdata, sdata = await asyncio.gather(
            self.api.channels.all(),
            self.api.channels.streams(),
        )

        c = {c['broadcaster_name']: ChannelInfo(**c, markup=markup, ansi=ansi) for c in cdata if 'type' not in c}
        s = {s['user_name']: FollowedStream(**s, markup=markup, ansi=ansi) for s in sdata if 'type' in s}
        self.online = len(s)
        return merge_data(c, s)

    @astimeit
    async def videos(self, user_id: str, markup: bool, ansi: bool) -> Iterable[FollowedContentVideo]:
        data = await self.api.content.get_videos(user_id=user_id)
        return (FollowedContentVideo(**video, markup=markup, ansi=ansi) for video in data)

    @astimeit
    async def clips(self, user_id: str, markup: bool, ansi: bool) -> Iterable[FollowedContentClip]:
        data = await self.api.content.get_clips(user_id=user_id)
        return (FollowedContentClip(**clip, markup=markup, ansi=ansi) for clip in data)

    @astimeit
    async def streams_by_game_id(self, game_id: str, markup: bool, ansi: bool) -> Iterable[FollowedStream]:
        logger.debug('getting streams by game_id: %s', game_id)
        data = await self.api.content.get_streams_by_game_id(game_id)
        return (FollowedStream(**item, markup=markup, ansi=ansi) for item in data)

    @astimeit
    async def games_by_query(self, query: str, markup: bool, ansi: bool) -> Iterable[Game]:
        data = await self.api.content.search_categories(query)
        return (Game(**item, markup=markup, ansi=ansi) for item in data)

    @astimeit
    async def channels_by_query(
        self, query: str, markup: bool, ansi: bool, live_only: bool = True
    ) -> Iterable[FollowedChannel]:
        data = await self.api.content.search_channels(query, live_only=live_only)
        data_sorted_by_live = sorted(data, key=lambda c: c['is_live'], reverse=True)
        return (Channel(**item, markup=markup, ansi=ansi) for item in data_sorted_by_live if item['game_name'])

    @astimeit
    async def top_streams(self, markup: bool, ansi: bool) -> Iterable[FollowedStream]:
        data = await self.api.content.get_top_streams()
        return (FollowedStream(**s, markup=markup, ansi=ansi) for s in data)

    @astimeit
    async def top_games(self, items_max: int, markup: bool, ansi: bool) -> Iterable[Category]:
        data = await self.api.content.get_top_games(items_max)
        return (Game(**g, markup=markup, asni=ansi) for g in data)

    @astimeit
    async def top_games_with_streams(self, markup: bool, ansi: bool) -> Mapping[str, Category]:
        max_games, max_streams = (30, 35)
        top_games = await self.top_games(max_games, markup, ansi)
        games_streams_data = await self._top_games_streams_data(top_games, max_games, max_streams)
        return create_categories(games_streams_data, markup, ansi)

    @astimeit
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
