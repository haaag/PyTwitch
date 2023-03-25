# twitch.py

from __future__ import annotations

from twitch.api import ChannelsAPI
from twitch.api import ClipsAPI
from twitch.api import TwitchAPI
from twitch.utils.menu import MenuUnicodes

# TODO:
# [ ] Add database for simples and fast request for data.


class TwitchClient:
    def __init__(self) -> None:
        self.api = TwitchAPI()
        self.channels = ChannelsAPI()
        self.clips = ClipsAPI()
        self.live_icon = MenuUnicodes.CIRCLE
        self.delimiter = MenuUnicodes.DELIMITER
