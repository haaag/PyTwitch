# api.py

from __future__ import annotations

import logging
import os
import sys
import typing
import warnings
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Iterable
from typing import Iterator
from typing import Union

import httpx
from dotenv import load_dotenv
from httpx import URL

from pytwitchify.constants import API_TWITCH_BASE_URL
from pytwitchify.content import FollowedContentClip
from pytwitchify.content import FollowedContentVideo
from pytwitchify.follows import FollowedChannel
from pytwitchify.follows import FollowedChannelInfo
from pytwitchify.follows import FollowedChannelLive
from pytwitchify.follows import SearchChannelsAPIResponse

if typing.TYPE_CHECKING:
    from pytwitchify.datatypes import HeaderTypes
    from pytwitchify.datatypes import QueryParamTypes
    from pytwitchify.datatypes import TwitchApiResponse

log = logging.getLogger(__name__)

load_dotenv()

MAX_ITEMS_PER_REQUEST = 100


class ValidationEnvError(Exception):
    pass


@dataclass
class TwitchApiCredentials:
    access_token: str
    client_id: str
    user_id: int

    def __post_init__(self):
        credentials = [self.access_token, self.client_id, self.user_id]
        if not all(env_var is not None and env_var != "" for env_var in credentials):
            raise ValidationEnvError("There's something wrong with the .env file")


class TwitchAPI:
    base_url: URL
    credentials: TwitchApiCredentials

    def __init__(self) -> None:
        self.credentials = self.validate_credentials()
        self.base_url = API_TWITCH_BASE_URL
        self.client = httpx.Client(headers=self._get_request_headers)

    def validate_credentials(self) -> TwitchApiCredentials:
        return TwitchApiCredentials(
            access_token=os.getenv("TWITCH_ACCESS_TOKEN"),  # type: ignore
            client_id=os.getenv("TWITCH_CLIENT_ID"),  # type: ignore
            user_id=os.getenv("TWITCH_USER_ID"),  # type: ignore
        )

    @property
    def _get_request_headers(self) -> HeaderTypes:
        return {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": self.credentials.client_id,
            "Authorization": "Bearer " + self.credentials.access_token,
        }

    def request_get(
        self,
        endpoint_url: URL,
        query_params: QueryParamTypes,
        limit: int = 200,
        quantity: int = 0,
    ) -> TwitchApiResponse:
        url = self.base_url.join(endpoint_url)

        query_params["first"] = MAX_ITEMS_PER_REQUEST
        log.debug("Params: %s", query_params)
        response = self.client.get(url, params=query_params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            error_msg = f"Error response {exc.response.status_code} {exc.request.url}"
            log.error(error_msg)
            sys.exit(1)
        else:
            data = response.json()
            quantity += len(data["data"])

        if data.get("pagination") and limit > quantity:
            query_params["after"] = data["pagination"]["cursor"]
            more_data = self.request_get(endpoint_url, query_params, quantity=quantity)["data"]
            if limit > quantity:
                data["data"] += more_data
        return data


class ContentAPI(TwitchAPI):
    def get_clips(self, user_id: str) -> Iterator[FollowedContentClip]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        ended_at = datetime.now().isoformat() + "Z"
        started_at = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
        endpoint = URL("clips")
        params = {
            "broadcaster_id": user_id,
            "started_at": started_at,
            "ended_at": ended_at,
        }
        data = self.request_get(endpoint, params)
        return (FollowedContentClip(**clip) for clip in data["data"])

    def get_videos(self, user_id: str, highlight: bool = False) -> Iterator[FollowedContentVideo]:
        """
        Gets information about one or more published videos.

        Args:
            user_id (str): The ID of the user.
            highlight (bool, optional): A flag indicating whether to retrieve only highlights (default is False).

        Returns:
            TwitchChannelVideos: An iterable containing information about the videos.
        """
        # https://dev.twitch.tv/docs/api/reference#get-videos
        endpoint = URL("videos")
        params = {"user_id": user_id, "period": "week", "type": "archive"}
        if highlight:
            params["type"] = "highlight"
        data = self.request_get(endpoint, params)
        return (FollowedContentVideo(**video) for video in data["data"])


class ChannelsAPI(TwitchAPI):
    content = ContentAPI()
    """
    A class for interacting with the Twitch Channels API.

    The Channels API allows users to retrieve information about channels,
    search for channels, and get a list of channels that the user follows.
    """

    def get_channels_live_beta(self) -> Iterable[FollowedChannelLive]:
        """
        Gets a list of live streams of broadcasters that the specified user follows.

        Returns:
            TwitchStreams: A list of live streams.
        """
        # https://dev.twitch.tv/docs/api/reference#get-followed-streams
        log.debug("Getting a list of live streams")
        endpoint = URL("streams/followed")
        params = {"user_id": self.credentials.user_id}
        channels = self.request_get(endpoint, params)
        return [FollowedChannelLive(**streamer) for streamer in channels["data"]]

    @property
    def get_channels_live(self) -> Iterable[FollowedChannelLive]:
        """
        Gets a list of live streams of broadcasters that the specified user follows.

        Returns:
            TwitchStreams: A list of live streams.
        """
        # https://dev.twitch.tv/docs/api/reference#get-followed-streams
        log.debug("Getting a list of live streams")
        endpoint = URL("streams/followed")
        params = {"user_id": self.credentials.user_id}
        channels = self.request_get(endpoint, params)
        return [FollowedChannelLive(**streamer) for streamer in channels["data"]]

    @property
    def channels(self) -> Iterable[FollowedChannel]:
        # https://dev.twitch.tv/docs/api/reference/#get-followed-channels
        log.debug("getting list that user follows")
        endpoint = URL("channels/followed")
        params = {"user_id": self.credentials.user_id}
        data = self.request_get(endpoint, params)["data"]
        return [FollowedChannel(**follow) for follow in data]

    def get_channel_info(self, user_id: str) -> FollowedChannelInfo:
        """Fetches information about one channel."""
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        log.debug("Getting information about channel")
        endpoint = URL("channels")
        params = {"broadcaster_id": user_id}
        data = self.request_get(endpoint, params)
        return FollowedChannelInfo(**data["data"][0])

    def get_channels_info(self, broadcaster_ids: list[str]) -> list[FollowedChannelInfo]:
        """
        Fetches information about list channels.

        Args:
            broadcaster_ids (str): The ID of the broadcaster.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        endpoint = URL("channels")
        params = {"broadcaster_id": broadcaster_ids}
        data = self.request_get(endpoint, params)["data"]
        return [FollowedChannelInfo(**broadcaster) for broadcaster in data]

    def search(self, query: str, live_only: bool = True) -> Iterable[SearchChannelsAPIResponse]:
        """
        Gets the channels that match the specified query.

        Args:
            query (str): The search query.
            live_only (bool, optional): A flag indicating whether to search only for live channels (default is True).
            maximum_items (int, optional): The maximum number of items to return (default is 20).

        Returns:
            Iterable[SearchChannelsAPIResponse]: An iterable containing information about the
            channels that match the search query.
        """
        # https://dev.twitch.tv/docs/api/reference#search-channels
        endpoint = URL("search/channels")
        params = {"query": query, "live_only": live_only}
        data = self.request_get(endpoint, params)
        return [SearchChannelsAPIResponse(**streamer) for streamer in data["data"]]

    def is_channel_online_by_userid(self, user_id: Union[str, list[str]]) -> bool:
        """Check if a user is currently streaming on Twitch."""
        # https://dev.twitch.tv/docs/api/reference#get-streams
        endpoint = URL("streams")
        params = {"user_id": user_id}
        # FIX:
        data = self.request_get(endpoint, params)["data"]
        __import__("pprint").pprint(data)
        return bool(self.request_get(endpoint, params)["data"])

    def is_channel_online(self, user_name: str) -> bool:
        """Check if a user is currently streaming on Twitch."""
        # https://dev.twitch.tv/docs/api/reference#get-streams
        user = self.get_channel_info_by_username(user_name)
        return self.is_channel_online_by_userid(user.user_id)

    def get_channel_info_by_username(self, user_name: str) -> FollowedChannelInfo:
        log.debug("getting '%s' user info", user_name)
        follows = {channel.name: channel for channel in self.channels}
        if user_name not in follows:
            log.error("user='%s' not found", user_name)
            raise ValueError(f"'{user_name=} not found")
        return self.get_channel_info(follows[user_name].user_id)
