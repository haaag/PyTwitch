# app.py
from __future__ import annotations

import logging
import sys
import typing
import webbrowser
from dataclasses import asdict
from typing import Any
from typing import Callable
from typing import Mapping
from typing import NamedTuple

from src.twitch import helpers
from src.twitch.constants import SEPARATOR
from src.twitch.constants import UserHitsEnter

if typing.TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface
    from pyselector.key_manager import Keybind

    from src.twitch.client import TwitchClient
    from src.twitch.content import FollowedContentClip
    from src.twitch.content import FollowedContentVideo
    from src.twitch.datatypes import TwitchChannel
    from src.twitch.datatypes import TwitchContent
    from src.twitch.follows import FollowedChannelInfo
    from src.twitch.follows import FollowedStream
    from src.twitch.player import Player
    from src.twitch.player import TwitchPlayableContent

logger = logging.getLogger(__name__)


class Keys(NamedTuple):
    channels: str
    categories: str
    clips: str
    videos: str
    chat: str
    information: str
    multi_selection: str


class TwitchApp:
    def __init__(self, client: TwitchClient, prompt: Callable, menu: MenuInterface, player: Player):
        self.client = client
        self.prompt = prompt
        self.menu = menu
        self.player = player

    def run(self) -> None:
        items, mesg = self.get_channels_and_streams()
        item, keycode = self.select_from_items(items=items, mesg=mesg)

        if keycode == UserHitsEnter(0) and item.playable:
            self.play(item)
            sys.exit()

        if not item.playable:
            item, keycode = self.show_channel_videos(item=item)

        keybind = self.get_key(keycode)
        keybind.callback(items=items, item=item)

    def multi_selection(self, **kwargs) -> None:
        self.menu.keybind.toggle_all()
        items = kwargs.get("items", self.client.streams)
        mesg = f"> Showing ({self.client.online}) streams."
        mesg += "\n>> Use 'Shift'+'Enter' for multi-select"
        selected, keycode = self.prompt(
            items=list(items.values()),
            mesg=mesg,
            multi_select=True,
            markup=self.client.markup,
        )
        for item_selected in selected:
            name = helpers.extract_key_from_str(item_selected, sep=SEPARATOR)
            item = self.get_item(items, name)
            if not item.playable:
                logger.info(f"{item.name=} is offline.")
                continue
            self.play(item)
        sys.exit(0)

    def get_item(self, items: dict[str, Any], name: str) -> Any:
        try:
            item = items[name]
        except KeyError as err:
            err_msg = f"item='{name}' not found"
            logger.error(err_msg)
            raise ValueError(err_msg) from err
        return item

    def show_categories(self, **kwargs) -> tuple[TwitchContent, int]:
        self.menu.keybind.toggle_all()
        categories = self.client.games
        mesg = f"> Showing ({len(categories)}) <categories> or <games>"
        category, keycode = self.select_from_items(items=categories, mesg=mesg)
        item, keycode = self.select_from_items(items=category.channels)
        if keycode != UserHitsEnter(0):
            self.menu.keybind.get_keybind_by_code(keycode).callback(items=category.channels)
        return item, keycode

    def select_from_items(self, items: Mapping[str, Any], mesg: str = "") -> tuple[TwitchContent, int]:
        item, keycode = self.prompt(
            items=list(items.values()),
            mesg=mesg,
            markup=self.client.markup,
        )
        name = helpers.extract_key_from_str(item, sep=SEPARATOR)
        return items[name], keycode

    def show_channel_videos(self, **kwargs) -> tuple[TwitchContent, int]:
        item: TwitchChannel = kwargs.pop("item")
        self.menu.keybind.toggle_all()
        videos, mesg = self.get_channel_videos(item=item)
        video_selected, keycode = self.select_from_items(items=videos, mesg=mesg)
        if keycode != UserHitsEnter(0):
            self.menu.keybind.get_keybind_by_code(keycode).callback(items=videos, item=video_selected)
        return video_selected, UserHitsEnter(0)

    def show_channel_clips(self, **kwargs) -> tuple[TwitchContent, int]:
        item: TwitchChannel = kwargs.pop("item")
        self.menu.keybind.toggle_all()
        clips, mesg = self.get_channel_clips(item=item)
        clip_selected, keycode = self.select_from_items(items=clips, mesg=mesg)
        if keycode != UserHitsEnter(0):
            self.menu.keybind.get_keybind_by_code(keycode).callback(items=clips)
        return clip_selected, UserHitsEnter(0)

    def get_channels_and_streams(self, **kwargs) -> tuple[dict[str, FollowedChannelInfo | FollowedStream], str]:
        data = self.client.channels_and_streams
        return data, f"> Showing ({self.client.online}) streams from {len(data)} channels"

    def get_channel_clips(self, **kwargs) -> tuple[dict[str, FollowedContentClip], str]:
        item: TwitchChannel = kwargs.pop("item")
        logger.info("processing user='%s' clips", item.name)
        clips = self.client.get_channel_clips(user_id=item.user_id)
        data = {c.key: c for c in clips}
        return data, f"> Showing ({len(data)}) clips from <{item.name}> channel"

    def get_channel_videos(self, **kwargs) -> tuple[dict[str, FollowedContentVideo], str]:
        item = kwargs.pop("item")
        videos = self.client.get_channel_videos(user_id=item.user_id)
        data = {v.key: v for v in videos}
        return data, f"> Showing ({len(data)}) videos from <{item.name}> channel"

    def play(self, follow) -> int:
        logger.warning(f"playing content {follow.url=}")
        process = self.player.play(follow)
        return process.returncode

    def record(self, follow: TwitchPlayableContent, path: str) -> int:
        logger.warning(f"recording content {follow.url=}")
        return self.player.record(follow, path)

    def toggle_key(self, binds: str | list[str]) -> None:
        if isinstance(binds, str):
            binds = [binds]
        for bind in binds:
            self.menu.keybind.get_keybind_by_bind(bind).toggle_hidden()

    def key_show(self, bind: str) -> None:
        self.menu.keybind.get_keybind_by_bind(bind).show()

    def key_hide(self, bind: str) -> None:
        self.menu.keybind.get_keybind_by_bind(bind).hide()

    def get_key(self, keycode: int) -> Keybind:
        return self.menu.keybind.get_keybind_by_code(keycode)

    def chat(self, **kwargs) -> None:
        item = kwargs.pop("item")
        webbrowser.open_new_tab(item.chat)
        sys.exit(0)

    def get_item_info(self, **kwargs) -> None:
        item: TwitchContent | TwitchChannel = kwargs["item"]
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

    def close(self) -> None:
        logger.debug("closing connection")
        self.client.api.client.close()
