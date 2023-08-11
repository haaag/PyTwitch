# api.py

from __future__ import annotations

import logging
import typing
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

import httpx
from httpx import URL

from src.twitch._exceptions import EnvValidationError
from src.twitch.constants import TWITCH_ACCESS_TOKEN
from src.twitch.constants import TWITCH_API_BASE_URL
from src.twitch.constants import TWITCH_CLIENT_ID
from src.twitch.constants import TWITCH_USER_ID

if typing.TYPE_CHECKING:
    from src.twitch.datatypes import HeaderTypes
    from src.twitch.datatypes import QueryParamTypes
    from src.twitch.datatypes import TwitchApiResponse

log = logging.getLogger(__name__)


MAX_ITEMS_PER_REQUEST = 100
DEFAULT_REQUESTED_ITEMS = 200


def validate_credentials(credentials: dict[str, str]) -> None:
    for key, value in credentials.items():
        if not value:
            err_msg = f"Environment variable {key!r} is not set"
            log.error(err_msg)
            raise EnvValidationError(err_msg)


@dataclass
class TwitchApiCredentials:
    access_token: str
    client_id: str
    user_id: str

    def to_dict(self) -> dict[str, str]:
        return self.__dict__


class API:
    base_url: URL
    credentials: TwitchApiCredentials
    client: httpx.Client

    def __init__(self) -> None:
        self.credentials = self.get_credentials()
        self.base_url = TWITCH_API_BASE_URL

        self.validate_credentials()
        self.load_client()

    def get_credentials(self) -> TwitchApiCredentials:
        return TwitchApiCredentials(
            access_token=TWITCH_ACCESS_TOKEN,  # type: ignore[arg-type]
            client_id=TWITCH_CLIENT_ID,  # type: ignore[arg-type]
            user_id=TWITCH_USER_ID,  # type: ignore[arg-type]
        )

    def validate_credentials(self) -> None:
        return validate_credentials(self.credentials.to_dict())

    def load_client(self) -> None:
        self.client = httpx.Client(headers=self._get_request_headers())

    def _get_request_headers(self) -> HeaderTypes:
        return {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": self.credentials.client_id,
            "Authorization": f"Bearer {self.credentials.access_token}",
        }

    def request_get(
        self,
        endpoint_url: URL,
        query_params: QueryParamTypes,
        requested_items: int = DEFAULT_REQUESTED_ITEMS,
        accumulated_items: int = 0,
    ) -> TwitchApiResponse:
        url = self.base_url.join(endpoint_url)

        query_params["first"] = min(MAX_ITEMS_PER_REQUEST, requested_items)
        log.debug("params: %s", query_params)
        response = self.client.get(url, params=query_params)
        response.raise_for_status()
        data = response.json()
        accumulated_items += len(data["data"])

        if data.get("pagination") and requested_items > accumulated_items:
            query_params["after"] = data["pagination"]["cursor"]
            remaining_items = requested_items - accumulated_items
            if remaining_items > 0:
                query_params["first"] = min(MAX_ITEMS_PER_REQUEST, remaining_items)
                more_data = self.request_get(
                    endpoint_url,
                    query_params,
                    requested_items=requested_items,
                    accumulated_items=accumulated_items,
                )
                data["data"] += more_data["data"][:remaining_items]
        return data


class Content:
    def __init__(self, api: API) -> None:
        self.api = api

    def get_clips(self, user_id: str) -> list[dict[str, Any]]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        log.debug("getting user_id='%s' clips", user_id)
        ended_at = datetime.now(tz=timezone.utc).isoformat() + "Z"
        started_at = (datetime.now(tz=timezone.utc) - timedelta(days=7)).isoformat() + "Z"
        endpoint = URL("clips")
        params = {
            "broadcaster_id": user_id,
            "started_at": started_at,
            "ended_at": ended_at,
        }
        response = self.api.request_get(endpoint, params, requested_items=100)
        data = response["data"]
        log.info("clips_len='%s'", len(data))
        return data

    def get_videos(self, user_id: str, highlight: bool = False) -> list[dict[str, Any]]:
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
        endpoint = URL("videos")
        params = {
            "user_id": user_id,
            "period": "week",
            "type": "archive",
        }
        if highlight:
            params["type"] = "highlight"
        response = self.api.request_get(endpoint, params, requested_items=100)
        data = response["data"]
        log.info("videos_len='%s'", len(data))
        return data


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
        log.debug("getting a list of live streams")
        endpoint = URL("streams/followed")
        params = {"user_id": self.api.credentials.user_id}
        response = self.api.request_get(endpoint, params)
        return response["data"]

    def get_channels(self) -> list[dict[str, Any]]:
        # https://dev.twitch.tv/docs/api/reference/#get-followed-channels
        log.debug("getting list that user follows")
        endpoint = URL("channels/followed")
        params = {"user_id": self.api.credentials.user_id}
        response = self.api.request_get(endpoint, params)
        return response["data"]

    def get_channel_info(self, user_id: str) -> list[dict[str, Any]]:
        """Fetches information about one channel."""
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        log.debug("getting information about channel")
        endpoint = URL("channels")
        params = {"broadcaster_id": user_id}
        response = self.api.request_get(endpoint, params)
        return response["data"]

    def get_channels_info(self, broadcaster_ids: list[str]) -> list[dict[str, Any]]:
        """
        Fetches information about list channels.

        Args:
            broadcaster_ids (str): The ID of the broadcaster.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        endpoint = URL("channels")
        params = {"broadcaster_id": broadcaster_ids}
        response = self.api.request_get(endpoint, params)
        return response["data"]


class TwitchApi(API):
    def __init__(self) -> None:
        super().__init__()
        self.channels = Channels(api=self)
        self.content = Content(api=self)
