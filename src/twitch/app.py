# app.py

from __future__ import annotations

import logging
import sys
import typing
import webbrowser
from dataclasses import asdict
from typing import Callable
from typing import NamedTuple
from typing import Union

from src.twitch import helpers
from src.twitch.constants import SEPARATOR

if typing.TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface
    from pyselector.key_manager import Keybind

    from src.twitch.client import TwitchClient
    from src.twitch.content import FollowedContentClip
    from src.twitch.content import FollowedContentVideo
    from src.twitch.follows import FollowedChannelInfo
    from src.twitch.follows import FollowedStream
    from src.twitch.player import Player
    from src.twitch.player import TwitchPlayableContent

log = logging.getLogger(__name__)


class Keys(NamedTuple):
    channels: str
    categories: str
    clips: str
    videos: str
    chat: str
    information: str


class App:
    def __init__(self, client: TwitchClient, prompt: Callable, menu: MenuInterface, player: Player, keys: Keys):
        self.client = client
        self.prompt = prompt
        self.menu = menu
        self.player = player
        self.key = keys

    def run(self) -> TwitchPlayableContent:
        channels, mesg = self.get_channels_and_streams()
        item, keycode = self.display(items=channels, mesg=mesg)

        while keycode != 0:
            keybind = self.menu.keybind.get_keybind_by_code(keycode)
            log.info(f"{keybind=}")
            items, mesg = keybind.callback(keybind=keybind, item=item)
            item, keycode = self.display(items=items, mesg=mesg)

        log.debug("return item='%s' from (self.run)", item.name)

        if hasattr(item, "live") and not item.live:
            # channel offline
            item = self.show_channel_videos(item=item)
        return item

    def display(self, items, mesg: str = ""):
        if not mesg:
            mesg = f"> Showing ({len(items)}) items"

        selected, keycode = self.prompt(
            items=list(items.values()),
            mesg=mesg,
            markup=self.client.markup,
        )

        name = helpers.extract_key_from_str(selected, sep=SEPARATOR)
        log.debug("name='%s' extracted from (self.display)", name)

        try:
            item = items[name]
        except KeyError as err:
            log.error("item='%s' not found", selected)
            raise ValueError(f"item='{selected}' not found") from err
        return item, keycode

    def show_categories(
        self, keybind: Keybind, **kwargs
    ) -> tuple[dict[str, Union[FollowedChannelInfo, FollowedStream]], str]:
        keybinds = self.menu.keybind.unregister_all()
        categories = self.client.games
        mesg = f"> Showing ({len(categories)}) <categories> or <games>"
        category, keycode = self.display(items=categories, mesg=mesg)

        for key in keybinds:
            self.menu.keybind.register(key)

        self.menu.keybind.get_keybind_by_bind(self.key.channels).toggle_hidden()
        data = category.channels
        return data, f"> Showing ({category.online}) streams from <{category.name}>"

    def show_channel_videos(self, **kwargs) -> TwitchPlayableContent:
        item = kwargs.pop("item")
        videos, mesg = self.get_channel_videos(item=item)
        video_selected, _ = self.display(items=videos, mesg=mesg)
        return video_selected

    def get_channels_and_streams(self, **kwargs) -> tuple[dict[str, Union[FollowedChannelInfo, FollowedStream]], str]:
        self.menu.keybind.get_keybind_by_bind(self.key.channels).toggle_hidden()
        data = self.client.channels_and_streams
        return data, f"> Showing ({self.client.online}) streams from {len(data)} channels"

    def get_channel_clips(self, **kwargs) -> tuple[dict[str, FollowedContentClip], str]:
        item = kwargs.pop("item")
        log.info("processing user='%s' clips", item.name)
        self.toggle_key([self.key.channels, self.key.clips, self.key.videos])
        clips = self.client.get_channel_clips(user_id=item.user_id)
        data = {c.key: c for c in clips}
        return data, f"> Showing ({len(data)}) clips from <{item.name}> channel"

    def get_channel_videos(self, **kwargs) -> tuple[dict[str, FollowedContentVideo], str]:
        item = kwargs.pop("item")
        self.toggle_key([self.key.channels, self.key.clips, self.key.videos])
        videos = self.client.get_channel_videos(user_id=item.user_id)
        data = {v.key: v for v in videos}
        return data, f"> Showing ({len(data)}) videos from <{item.name}> channel"

    def play(self, follow) -> int:
        log.warning(f"playing content {follow.url=}")
        return self.player.play(follow)

    def record(self, follow: TwitchPlayableContent, path: str) -> int:
        log.warning(f"recording content {follow.url=}")
        return self.player.record(follow, path)

    def toggle_key(self, binds: Union[str, list[str]]) -> None:
        if isinstance(binds, str):
            binds = [binds]
        for bind in binds:
            self.menu.keybind.get_keybind_by_bind(bind).toggle_hidden()

    def show_key(self, bind: str) -> None:
        self.menu.keybind.get_keybind_by_bind(bind).show()

    def hide_key(self, bind: str) -> None:
        self.menu.keybind.get_keybind_by_bind(bind).hide()

    def chat(self, **kwargs) -> None:
        item = kwargs.pop("item")
        webbrowser.open_new_tab(item.chat)
        sys.exit(0)

    def get_item_info(self, **kwargs) -> None:
        item = kwargs.get("item")
        item_dict = asdict(item)
        formatted_item = helpers.stringify_dict(item_dict, sep=SEPARATOR)
        formatted_item.append(f"{'url':<18}{SEPARATOR}\t{item.url:<30}")
        selected, keycode = self.prompt(
            items=formatted_item,
            mesg="Item information",
            markup=False,
        )
        selected = selected.split(SEPARATOR, maxsplit=1)[1].strip()
        helpers.copy_to_clipboard(selected)
        sys.exit(0)
