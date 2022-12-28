# twitch.py

from typing import Text

from twitch.api import ChannelsAPI
from twitch.api import ClipsAPI
from twitch.api import TwitchAPI
from twitch.datatypes import TwitchStreamLive
from twitch.datatypes import TwitchStreams
from twitch.utils import helpers
from twitch.utils.menu import MenuUnicodes


class TwitchClient:
    def __init__(self, live_icon: Text = MenuUnicodes.CIRCLE) -> None:
        self.api = TwitchAPI()
        self.channels = ChannelsAPI()
        self.clips = ClipsAPI()
        self.live_icon = live_icon

    @property
    def channels_live(self) -> TwitchStreams:
        return self.channels.followed_streams_live

    @property
    def channels_live_for_menu(self) -> TwitchStreams:
        channels = self.channels.followed_streams_live
        for stream in channels:
            live_since = helpers.calculate_live_time(stream.started_at)
            stream.user_name = f"{self.live_icon} {stream.user_name} | {stream.title[:60]} ({live_since})"
        return channels

    def insert_live_icon(self, stream: TwitchStreamLive) -> TwitchStreamLive:
        stream.user_name = f"{self.live_icon} {stream.user_name}"
        return stream

    # def if_online(self, saved_channels: TwitchChannels, live_channels: TwitchStreams) -> TwitchChannels:
    #     """Checks if online channel is in offline channel list."""
    #     for (saved, online) in itertools.product(saved_channels, live_channels):
    #         if str(saved.user_id) == online.user_id:
    #             saved.user_login = online.user_login
    #     return saved_channels

    # @property
    # def subcriptions(self) -> None:
    #     raise NotImplementedError()

    # def info_channel(self, channel_id: int) -> BroadcasterInfo:
    #     return self.channels.information(user_id=channel_id)

    # def add_channel(self, channel_name: str, maximum_items: int = 50) -> TwitchChannelList:
    #     channels_found: list[str] = []
    #     channels = self.channels.search(query=channel_name, live_only=False, maximum_items=maximum_items)
    #     for idx, channel in enumerate(channels):
    #         name = channel.broadcaster_login
    #         title = channel.title[:79]
    #         channels_found.append(f"{idx} | {name} - {title}")
    #     return channels_found

    # @property
    # def channels_saved(self) -> TwitchChannels:
    #     return self.api.saved_channels()

    # @property
    # def channels_old(self) -> TwitchChannels:
    #     """Returns channel list, online and saved"""
    #     return self.if_online(self.channels_saved, self.channels_live_for_menu)

    # def save_channels(self, data: TwitchStreams) -> None:
    #     """Save channels to JSON file."""
    #     self.db.update_channels(data)
    #
    # def edit_channel(self, channel_id: int) -> None:
    #     raise NotImplementedError()
    #

    # def update_channels(self) -> None:
    #     """Update JSON file with new channels."""
    #     raise NotImplementedError()
