# twitch.py

from typing import Text

from twitch.api import ChannelsAPI
from twitch.api import ClipsAPI
from twitch.api import TwitchAPI
from twitch.datatypes import TwitchStreams
from twitch.utils import helpers
from twitch.utils.menu import MenuUnicodes

# TODO:
# [ ] Add database for simples and fast request for data.


class TwitchClient:
    def __init__(self, live_icon: Text = MenuUnicodes.CIRCLE) -> None:
        self.api = TwitchAPI()
        self.channels = ChannelsAPI()
        self.clips = ClipsAPI()
        self.live_icon = live_icon

    @property
    def channels_live_for_menu(self) -> TwitchStreams:
        """
        Return a list of live streams that are followed by the user,
        with the live icon and live time appended to their names.
        """
        channels = self.channels.followed_streams_live
        for stream in channels:
            live_since = helpers.calculate_live_time(stream.started_at)
            stream.user_name = f"{self.live_icon} {stream.user_name} | {stream.title[:60]} ({live_since})"
        return channels
