# api.py

from __future__ import annotations

import logging
import typing
from dataclasses import dataclass
from typing import Any
from typing import Iterator

import httpx
from httpx import URL
from twitch._exceptions import EnvValidationError
from twitch.constants import TWITCH_API_BASE_URL

if typing.TYPE_CHECKING:
    from twitch.datatypes import HeaderTypes
    from twitch.datatypes import QueryParamTypes
    from twitch.datatypes import TwitchApiResponse

log = logging.getLogger(__name__)


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


@dataclass
class Credentials:
    access_token: str
    client_id: str
    user_id: str

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

    def validate(self) -> None:
        return _validate_credentials(self.to_dict())


class API:
    base_url: URL
    client: httpx.Client

    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials
        self.base_url = TWITCH_API_BASE_URL

    def load_client(self) -> None:
        self.client = httpx.Client(headers=self._get_request_headers())

    def _get_request_headers(self) -> HeaderTypes:
        return {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': self.credentials.client_id,
            'Authorization': f'Bearer {self.credentials.access_token}',
        }

    def _set_query_params(self, query_params: QueryParamTypes, requested_items: int) -> QueryParamTypes:
        query_params['first'] = min(MAX_ITEMS_PER_REQUEST, requested_items)
        log.debug('params: %s', query_params)
        return query_params

    def send_request(self, url: URL, query_params: QueryParamTypes, timeout: int) -> httpx.Response:
        response = self.client.get(url, params=query_params, timeout=timeout)
        response.raise_for_status()
        return response

    def _has_pagination(self, data: TwitchApiResponse) -> bool:
        return data.get('pagination', {}).get('cursor') is not None

    def request_get(
        self,
        endpoint_url: URL,
        query_params: QueryParamTypes,
        requested_items: int = DEFAULT_REQUESTED_ITEMS,
        accumulated_items: int = 0,
    ) -> TwitchApiResponse:
        url = self.base_url.join(endpoint_url)
        query_params = self._set_query_params(query_params, requested_items)
        response = self.send_request(url, query_params, timeout=5)
        data = response.json()
        accumulated_items += len(data['data'])

        if not self._has_pagination(data):
            return data

        if requested_items >= accumulated_items:
            next_cursor = data['pagination']['cursor']
            remaining_items = requested_items - accumulated_items

            query_params['after'] = next_cursor
            query_params['first'] = min(MAX_ITEMS_PER_REQUEST, remaining_items)
            more_data = self.request_get(
                endpoint_url=endpoint_url,
                query_params=query_params,
                requested_items=requested_items,
                accumulated_items=accumulated_items,
            )
            data['data'] += more_data['data'][:remaining_items]
        return data


class Content:
    def __init__(self, api: API) -> None:
        self.api = api

    def get_clips(self, user_id: str) -> list[dict[str, Any]]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        endpoint = URL('clips')
        params = {'broadcaster_id': user_id, 'is_featured': True}
        response = self.api.request_get(
            endpoint,
            params,
            requested_items=MAX_ITEMS_PER_REQUEST,
        )
        data = response['data']
        log.info("got user_id='%s' clips len='%s'", user_id, len(data))
        return data

    def get_videos(self, user_id: str) -> list[dict[str, Any]]:
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
        response = self.api.request_get(endpoint, params, requested_items=75)
        data = response['data']
        log.info("videos_len='%s'", len(data))
        return data

    def search_categories(self, query: str) -> dict[str, Any]:
        """
        Gets the games or categories that match the specified query.
        """
        # https://dev.twitch.tv/docs/api/reference/#search-categories
        log.debug(f"searching for categories with query='{query}'")
        endpoint = URL('search/categories')
        params = {'query': query}
        response = self.api.request_get(endpoint, params)
        return response['data']

    def search_channels(self, query: str, live_only: bool = True) -> dict[str, Any]:
        """
        Gets the channels that match the specified query and have
        streamed content within the past 6 months.
        """
        # https://dev.twitch.tv/docs/api/reference/#search-channels
        log.debug(f"searching for channels with query='{query}'")
        endpoint = URL('search/channels')
        params = {'query': query, 'live_only': live_only}
        response = self.api.request_get(endpoint, params)
        return response['data']

    def get_streams_by_game_id(self, game_id: int, max_items: int = DEFAULT_REQUESTED_ITEMS) -> dict[str, Any]:
        """
        Gets a list of all streams.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-streams
        log.debug(f"getting streams from game_id='{game_id}'")
        endpoint = URL('streams')
        params = {'game_id': game_id}
        response = self.api.request_get(endpoint, params, requested_items=max_items)
        return response['data']

    def get_top_streams(self) -> dict[str, Any]:
        """
        Gets a list of all streams.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-streams
        endpoint = URL('streams')
        response = self.api.request_get(endpoint, query_params={}, requested_items=100)
        log.debug("top_streams_len='%s'", len(response['data']))
        return response['data']

    def get_games_info(self, game_ids: list[str]) -> list[dict[str, Any]]:
        """
        Gets information about specified categories or games.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-games
        data: list[dict[str, Any]] = []
        endpoint = URL('games')
        for batch in _group_into_batches(game_ids, MAX_ITEMS_PER_REQUEST):
            response = self.api.request_get(endpoint, {'id': batch})
            data.extend(response.get('data', []))
        log.debug("games_info_len='%s'", len(data))
        return data

    def get_top_games(self) -> dict[str, Any]:
        """
        Gets information about all broadcasts on Twitch.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-top-games
        endpoint = URL('games/top')
        response = self.api.request_get(endpoint, query_params={}, requested_items=35)
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

    def get_streams(self) -> list[dict[str, Any]]:
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
        response = self.api.request_get(endpoint, params, requested_items=max_followed_streams)
        return response['data']

    def get_all(self) -> list[dict[str, Any]]:
        """
        Gets a list of broadcasters that the specified user follows.
        """
        # https://dev.twitch.tv/docs/api/reference/#get-followed-channels
        max_followed_channels = 500
        log.debug(f'getting list that user follows, max={max_followed_channels}')
        endpoint = URL('channels/followed')
        params = {'user_id': self.api.credentials.user_id}
        response = self.api.request_get(endpoint, params, requested_items=max_followed_channels)
        return response['data']

    def get_info(self, user_id: str) -> list[dict[str, Any]]:
        """
        Fetches information about one channel.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        log.debug('getting information about channel')
        endpoint = URL('channels')
        params = {'broadcaster_id': user_id}
        response = self.api.request_get(endpoint, params)
        return response['data']

    def get_info_by_list(self, broadcaster_ids: list[str]) -> list[dict[str, Any]]:
        """
        Gets information about more channels.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        data: list[dict[str, Any]] = []
        endpoint = URL('channels')

        for batch in _group_into_batches(broadcaster_ids, MAX_ITEMS_PER_REQUEST):
            response = self.api.request_get(endpoint, {'broadcaster_id': batch})
            data.extend(response.get('data', []))
        return data


class TwitchApi(API):
    def __init__(self, credentials: Credentials) -> None:
        super().__init__(credentials)
        self.channels = Channels(api=self)
        self.content = Content(api=self)
