# twitch.py

from __future__ import annotations

from .api import ChannelsAPI
from .api import ClipsAPI
from .api import TwitchAPI
from .utils.menu import MenuUnicodes


class TwitchClient:
    def __init__(self) -> None:
        self.api = TwitchAPI()
        self.channels = ChannelsAPI()
        self.clips = ClipsAPI()
        self.live_icon = MenuUnicodes.CIRCLE
        self.delimiter = MenuUnicodes.DELIMITER
