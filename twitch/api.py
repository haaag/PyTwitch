# api.py

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Generator
from typing import Iterable
from typing import Iterator

import httpx
from dotenv import load_dotenv
from httpx import URL

from twitch.datatypes import BroadcasterInfo
from twitch.datatypes import ChannelUserFollows
from twitch.datatypes import HeaderTypes
from twitch.datatypes import QueryParamTypes
from twitch.datatypes import SearchChannelsAPIResponse
from twitch.datatypes import TwitchApiResponse
from twitch.datatypes import TwitchChannelSchedule
from twitch.datatypes import TwitchChannelVideo
from twitch.datatypes import TwitchClip
from twitch.datatypes import TwitchStreamLive
from twitch.datatypes import TwitchStreams
from twitch.datatypes import ValidationEnvError
from twitch.utils.colors import Color as C
from twitch.utils.logger import get_logger

log = get_logger(__name__)

load_dotenv()

# TODO:
# [X] Remove DB class from api


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
        self.base_url = URL("https://api.twitch.tv/helix/")

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

    @property
    def client(self) -> httpx.Client:
        return httpx.Client(headers=self._get_request_headers)

    def request_get(
        self,
        endpoint_url: URL,
        query_params: QueryParamTypes,
    ) -> TwitchApiResponse:
        url = self.base_url.join(endpoint_url)
        response = self.client.get(url, params=query_params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            error_url = C.info(str(exc.request.url))
            error_response = C.error(f"Error response {exc.response.status_code}")
            log.info("%s %s", error_response, error_url)
            sys.exit(1)
        else:
            data = response.json()

        if data.get("pagination"):
            query_params["after"] = data["pagination"]["cursor"]  # type: ignore
            data["data"] += self.request_get(endpoint_url, query_params)["data"]
        return data


class ChannelsAPI(TwitchAPI):
    """
    A class for interacting with the Twitch Channels API.

    The Channels API allows users to retrieve information about channels,
    search for channels, and get a list of channels that the user follows.
    """

    @property
    def followed_streams_live(self) -> TwitchStreams:
        """
        Gets a list of live streams of broadcasters that the specified user follows.

        Returns:
            TwitchStreams: A list of live streams.
        """
        # https://dev.twitch.tv/docs/api/reference#get-followed-streams
        endpoint = URL("streams/followed")
        params = {"user_id": self.credentials.user_id}
        channels = self.request_get(endpoint, params)
        return [TwitchStreamLive(**streamer) for streamer in channels["data"]]

    @property
    def follows(self) -> Iterable[ChannelUserFollows]:
        """
        Gets information about channels that user follows.

        Returns:
            Iterable[ChannelUserFollows]: An iterable containing information about the channels that the user follows.
        """
        # https://dev.twitch.tv/docs/api/reference#get-users-follows
        endpoint = URL("users/follows")
        params = {"from_id": self.credentials.user_id}
        data = self.request_get(endpoint, params)["data"]
        return [ChannelUserFollows(**user) for user in data]

    def schedule(self, user_id: str) -> TwitchChannelSchedule:
        # FIX: I think, no one uses this feature.
        """
        Gets the broadcaster’s streaming schedule.

        Args:
            user_id (str): The ID of the broadcaster.

        Returns:
            TwitchChannelSchedule: The streaming schedule for the specified broadcaster.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-stream-schedule
        # endpoint = URL("schedule")
        # params = {"broadcaster_id": user_id}
        # schedule = self.request_get(endpoint, params)
        raise NotImplementedError()

    def information(self, user_id: str) -> BroadcasterInfo:
        """
        Gets information about one channel.

        Args:
            user_id (str): The ID of the broadcaster.

        Returns:
            BroadcasterInfo: Information about the specified broadcaster.
        """
        # https://dev.twitch.tv/docs/api/reference#get-channel-information
        endpoint = URL("channels")
        params = {"broadcaster_id": user_id}
        data = self.request_get(endpoint, params)
        return BroadcasterInfo(**data["data"][0])

    def search(
        self, query: str, live_only: bool = True, maximum_items: int = 20
    ) -> Iterable[SearchChannelsAPIResponse]:
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
        params = {"first": maximum_items, "query": query, "live_only": live_only}
        data = self.request_get(endpoint, params)
        return [SearchChannelsAPIResponse(**streamer) for streamer in data["data"]]

    def get_videos(self, user_id: str, highlight: bool = False) -> Generator[TwitchChannelVideo, None, None]:
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
        params = {"user_id": user_id, "period": "week", "type": "archive", "first": 100}
        if highlight:
            params["type"] = "highlight"
        data = self.request_get(endpoint, params)
        return (TwitchChannelVideo(**video) for video in data["data"])

    def is_online(self, user_id: str) -> bool:
        """Check if a user is currently streaming on Twitch."""
        # https://dev.twitch.tv/docs/api/reference#get-streams
        endpoint = URL("streams")
        params = {"user_id": user_id}
        return bool(self.request_get(endpoint, params)["data"])


class ClipsAPI(TwitchAPI):
    def get_clips_list_comprehension(self, user_id: str) -> list[TwitchClip]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        ended_at = datetime.now().isoformat() + "Z"
        started_at = (datetime.now() - timedelta(days=5)).isoformat() + "Z"
        endpint = URL("clips")
        params = {"broadcaster_id": user_id, "first": 100, "started_at": started_at, "ended_at": ended_at}
        data = self.request_get(endpint, params)
        return [TwitchClip(**clip) for clip in data["data"]]

    def get_clips(self, user_id: str) -> Iterator[TwitchClip]:
        """Gets one or more video clips that were captured from streams."""
        # https://dev.twitch.tv/docs/api/reference#get-clips
        ended_at = datetime.now().isoformat() + "Z"
        started_at = (datetime.now() - timedelta(days=5)).isoformat() + "Z"
        endpint = URL("clips")
        params = {"broadcaster_id": user_id, "started_at": started_at, "ended_at": ended_at, "first": 100}
        data = self.request_get(endpint, params)
        return (TwitchClip(**clip) for clip in data["data"])
