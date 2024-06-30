# api.py

from __future__ import annotations

import logging
import os
import typing
from pathlib import Path
from typing import Any
from typing import Iterator

import httpx
from dotenv import load_dotenv
from httpx import URL
from pydantic import BaseModel
from tenacity import before_sleep_log
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed
from twitch._exceptions import EnvValidationError
from twitch.constants import TWITCH_API_BASE_URL

if typing.TYPE_CHECKING:
    from twitch.datatypes import HeaderTypes
    from twitch.datatypes import QueryParamTypes
    from twitch.datatypes import TwitchApiResponse

log = logging.getLogger(__name__)


RETRY_ATTEMPTS = 3
RETRY_DELAY = 1
MAX_ITEMS_PER_REQUEST = 100
DEFAULT_REQUESTED_ITEMS = 200


def _group_into_batches(ids: list[str], batch_size: int) -> Iterator[list[str]]:
    """
    Splits a list into batches of the maximum size allowed by the API.
    """
    for i in range(0, len(ids), batch_size):
        yield ids[i : i + batch_size]


def _validate_credentials(credentials: dict[str, str]) -> None:
    """
    Validates that all required environment variables are set.

    Raises:
        EnvValidationError: If any required variable is not set.
    """
    for k, v in credentials.items():
        if not v:
            err_msg = f'Missing required environment variable: {k}'
            raise EnvValidationError(err_msg)


def load_envs(filepath: str | None = None) -> None:
    """Load envs if path"""
    if not filepath:
        log.info('env: no env filepath specified')
        log.info('env: loading from .env or exported env vars')
        load_dotenv()
        return

    envfilepath = Path().absolute() / Path(filepath)
    if not envfilepath.exists():
        err = f'{envfilepath=!s} not found'
        raise EnvValidationError(err)
    if not envfilepath.is_file():
        err = f'{envfilepath=!s} is not a file'
        raise EnvValidationError(err)

    log.info(f'env: loading envs from {envfilepath=!s}')
    load_dotenv(dotenv_path=envfilepath.as_posix())


class Credentials(BaseModel):
    access_token: str | None
    client_id: str | None
    user_id: str | None

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

    def validate(self) -> None:
        return _validate_credentials(self.to_dict())

    @classmethod
    def load(cls, file: str) -> Credentials:
        load_envs(file)
        access_token = os.environ.get('TWITCH_ACCESS_TOKEN')
        client_id = os.environ.get('TWITCH_CLIENT_ID')
        user_id = os.environ.get('TWITCH_USER_ID')
        return cls(access_token=access_token, client_id=client_id, user_id=user_id)


class API:
    base_url: URL
    client: httpx.AsyncClient

    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials
        self.base_url = TWITCH_API_BASE_URL

    async def load_client(self) -> None:
        self.client = httpx.AsyncClient(headers=self._get_request_headers())

    def _get_request_headers(self) -> HeaderTypes:
        return {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': self.credentials.client_id,
            'Authorization': f'Bearer {self.credentials.access_token}',
        }

    def _set_params(self, params: QueryParamTypes, requested_items: int) -> QueryParamTypes:
        params['first'] = min(MAX_ITEMS_PER_REQUEST, requested_items)
        log.debug('params: %s', params)
        return params

    async def close(self) -> None:
        log.debug('closing async client connection')
        if self.client:
            await self.client.aclose()
            self.client = None

    async def send_request(self, url: URL, query_params: QueryParamTypes, timeout: int = 5) -> httpx.Response:
        r = await self.client.get(url, params=query_params, timeout=timeout)
        r.raise_for_status()
        return r

    def _has_pagination(self, data: TwitchApiResponse) -> bool:
        return data.get('pagination', {}).get('cursor') is not None

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_fixed(RETRY_DELAY),
        before_sleep=before_sleep_log(log, logging.WARN),
    )
    async def request_get(
        self,
        endpoint_url: URL,
        params: QueryParamTypes,
        max_items: int = DEFAULT_REQUESTED_ITEMS,
        items_collected: int = 0,
    ) -> TwitchApiResponse:
        url = self.base_url.join(endpoint_url)
        query_params_dict = self._set_params(params, max_items)
        response = await self.send_request(url, query_params_dict, timeout=10)
        data = response.json()
        items_collected += len(data['data'])

        if not self._has_pagination(data):
            return data

        if max_items >= items_collected:
            next_cursor = data['pagination']['cursor']
            remaining_items = max_items - items_collected

            params['after'] = next_cursor
            params['first'] = min(MAX_ITEMS_PER_REQUEST, remaining_items)
            more_data = await self.request_get(
                endpoint_url=endpoint_url,
                params=params,
                max_items=max_items,
                items_collected=items_collected,
            )
            data['data'].extend(more_data['data'][:remaining_items])
        return data


class Content:
    def __init__(self, api: API) -> None:
        self.api = api

    async def get_clips(self, user_id: str) -> list[dict[str, Any]]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        endpoint = URL('clips')
        params = {'broadcaster_id': user_id, 'is_featured': True}
        response = await self.api.request_get(
            endpoint,
            params,
            max_items=MAX_ITEMS_PER_REQUEST,
        )
        data = response['data']
        log.info("got user_id='%s' clips len='%s'", user_id, len(data))
        return data

    async def get_videos(self, user_id: str) -> list[dict[str, Any]]:
        """
        Gets information about one or more published videos.

        Args:
            user_id (str): The ID of the user.
            highlight (bool, optional): A flag indicating whether to retrieve only highlights (default is False).

        Returns:
            TwitchChannelVideos: An iterable containing information about the videos.
        """
        # https://dev.twitch.tv/docs/api/reference#get-videos
        log.debug("getting user_id='%s' videos", user_id)
        endpoint = URL('videos')
        params = {
            'user_id': user_id,
            'period': 'week',
            'type': 'archive',
        }
        response = await self.api.request_get(endpoint, params, max_items=50)
        data = response['data']
        log.info("got user_id='%s' videos len='%s'", user_id, len(data))
        return data

    async def search_categories(self, query: str) -> dict[str, Any]:
        """
        Gets the games or categories that match the specified query.
        """
        # https://dev.twitch.tv/docs/api/reference/#search-categories
        log.debug(f"searching for categories with query='{query}'")
        endpoint = URL('search/categories')
        params = {'query': query}
        response = await self.api.request_get(endpoint, params)
        return response['data']

    async def search_channels(self, query: str, live_only: bool = True) -> dict[str, Any]:
        """
        Gets the channels that match the specified query and have
        streamed content within the past 6 months.
        """
        # https://dev.twitch.tv/docs/api/reference/#search-channels
        log.debug(f"searching for channels with query='{query}'")
        endpoint = URL('search/channels')
        params = {'query': query, 'live_only': live_only}
        response = await self.api.request_get(endpoint, params)
        return response['data']

    async def get_streams_by_game_id(self, game_id: int, max_items: int = DEFAULT_REQUESTED_ITEMS) -> dict[str, Any]:
        """
        Gets a list of all streams.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-streams
        log.debug(f"getting streams from game_id='{game_id}'")
        endpoint = URL('streams')
        params = {'game_id': game_id}
        response = await self.api.request_get(endpoint, params, max_items=max_items)
        return response['data']

    async def get_top_streams(self) -> dict[str, Any]:
        """
        Gets a list of all streams.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-streams
        endpoint = URL('streams')
        response = await self.api.request_get(endpoint, params={}, max_items=100)
        log.debug("top_streams_len='%s'", len(response['data']))
        return response['data']

    async def get_games_info(self, game_ids: list[str]) -> list[dict[str, Any]]:
        """
        Gets information about specified categories or games.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-games
        data: list[dict[str, Any]] = []
        endpoint = URL('games')
        for batch in _group_into_batches(game_ids, MAX_ITEMS_PER_REQUEST):
            response = await self.api.request_get(endpoint, {'id': batch})
            data.extend(response.get('data', []))
        log.debug("games_info_len='%s'", len(data))
        return data

    async def get_top_games(self, items_max: int = MAX_ITEMS_PER_REQUEST) -> dict[str, Any]:
        """
        Gets information about all broadcasts on Twitch.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-top-games
        endpoint = URL('games/top')
        response = await self.api.request_get(endpoint, params={}, max_items=items_max)
        log.debug("top_games_len='%s'", len(response['data']))
        return response['data']


class Channels:
    def __init__(self, api: API) -> None:
        self.api = api

    """
    A class for interacting with the Twitch Channels API.

    The Channels API allows users to retrieve information about channels,
    search for channels, and get a list of channels that the user follows.
    """

    async def streams(self) -> list[dict[str, Any]]:
        """
        Gets a list of live streams of broadcasters that the specified user follows.

        Returns:
            TwitchStreams: A list of live streams.
        """
        # https://dev.twitch.tv/docs/api/reference#get-followed-streams
        max_followed_streams = 500
        log.debug(f'getting a list of live streams, max={max_followed_streams}')
        endpoint = URL('streams/followed')
        params = {'user_id': self.api.credentials.user_id}
        response = await self.api.request_get(endpoint, params, max_items=max_followed_streams)
        return response['data']

    async def all(self) -> list[dict[str, Any]]:
        """
        Gets a list of broadcasters that the specified user follows.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-followed-channels
        max_followed_channels = 500
        log.debug(f'getting list that user follows, max={max_followed_channels}')
        endpoint = URL('channels/followed')
        params = {'user_id': self.api.credentials.user_id}
        response = await self.api.request_get(endpoint, params, max_items=max_followed_channels)
        return response['data']

    async def ids(self) -> list[int]:
        """
        Gets a list of broadcasters's ids that the specified user follows.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-followed-channels
        max_followed_channels = 500
        log.debug(f'getting list that user follows, max={max_followed_channels}')
        endpoint = URL('channels/followed')
        params = {'user_id': self.api.credentials.user_id}
        response = await self.api.request_get(endpoint, params, max_items=max_followed_channels)
        return [c['broadcaster_id'] for c in response['data']]

    async def get_info(self, user_id: str) -> list[dict[str, Any]]:
        """
        Fetches information about one channel.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        log.debug('getting information about channel')
        endpoint = URL('channels')
        params = {'broadcaster_id': user_id}
        response = await self.api.request_get(endpoint, params)
        return response['data']

    async def info_ids(self, broadcaster_ids: list[str]) -> list[dict[str, Any]]:
        """
        Gets information about more channels.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        data: list[dict[str, Any]] = []
        endpoint = URL('channels')

        for batch in _group_into_batches(broadcaster_ids, MAX_ITEMS_PER_REQUEST):
            response = await self.api.request_get(endpoint, {'broadcaster_id': batch})
            data.extend(response.get('data', []))
        return data


class TwitchApi(API):
    def __init__(self, credentials: Credentials) -> None:
        super().__init__(credentials)
        self.channels = Channels(api=self)
        self.content = Content(api=self)
