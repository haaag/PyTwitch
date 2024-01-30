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

from twitch import helpers
from twitch.constants import SEPARATOR
from twitch.constants import UserCancelSelection
from twitch.constants import UserConfirmsSelection

if typing.TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface
    from pyselector.key_manager import Keybind
    from twitch.client import TwitchClient
    from twitch.content import FollowedContentClip
    from twitch.content import FollowedContentVideo
    from twitch.datatypes import TwitchChannel
    from twitch.datatypes import TwitchContent
    from twitch.follows import FollowedChannelInfo
    from twitch.follows import FollowedStream
    from twitch.player import Player
    from twitch.player import TwitchPlayableContent

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

    def show_content(self, **kwargs) -> None:
        items, mesg = self.get_channels_and_streams()
        item, keycode = self.select_from_items(items=items, mesg=mesg)

        if keycode == UserCancelSelection(1):
            sys.exit(keycode)

        if not item.playable:
            return self.show_channel_videos(item=item)

        if keycode == UserConfirmsSelection(0):
            returncode = self.play(item)
            sys.exit(returncode)

        keybind = self.get_key(keycode)
        return keybind.callback(items=items, item=item)

    def show_channel_videos(self, **kwargs) -> None:
        item: TwitchChannel = kwargs.pop("item")
        self.menu.keybind.toggle_all()
        videos, mesg = self.get_channel_videos(item=item)
        self.show_and_play(items=videos, mesg=mesg)

    def show_channel_clips(self, **kwargs) -> None:
        # FIXME:
        item: TwitchChannel = kwargs.pop("item")
        self.menu.keybind.toggle_all()
        clips, mesg = self.get_channel_clips(item=item)
        self.show_and_play(items=clips, mesg=mesg)

    def show_categories(self, **kwargs) -> None:
        self.menu.keybind.toggle_all()
        categories = self.client.games
        mesg = f"> Showing ({len(categories)}) <categories> or <games>"
        category, keycode = self.select_from_items(items=categories, mesg=mesg)
        self.show_and_play(category.channels)

    def show_and_play(self, items: Mapping[str, TwitchPlayableContent], mesg: str = "") -> None:
        item, keycode = self.select_from_items(items=items, mesg=mesg)
        if keycode == UserCancelSelection(1):
            return
        if keycode != UserConfirmsSelection(0):
            self.menu.keybind.get_keybind_by_code(keycode).callback(items=items)
        self.play(item)

    def get_channels_and_streams(self, **kwargs) -> tuple[Mapping[str, FollowedChannelInfo | FollowedStream], str]:
        data = self.client.channels_and_streams
        return data, f"> Showing ({self.client.online}) streams from {len(data)} channels"

    def get_channel_clips(self, **kwargs) -> tuple[Mapping[str, FollowedContentClip], str]:
        item: TwitchChannel = kwargs.pop("item")
        logger.info("processing user='%s' clips", item.name)
        clips = self.client.get_channel_clips(user_id=item.user_id)
        data = {c.key: c for c in clips}
        return data, f"> Showing ({len(data)}) clips from <{item.name}> channel"

    def get_channel_videos(self, **kwargs) -> tuple[Mapping[str, FollowedContentVideo], str]:
        item = kwargs.pop("item")
        videos = self.client.get_channel_videos(user_id=item.user_id)
        data = {v.key: v for v in videos}
        return data, f"> Showing ({len(data)}) videos from <{item.name}> channel"

    def select_from_items(self, items: Mapping[str, Any], mesg: str = "") -> tuple[Any, int]:
        item, keycode = self.prompt(
            items=list(items.values()),
            mesg=mesg,
            markup=self.client.markup,
        )
        return item, keycode

    def old_select_from_items(self, items: Mapping[str, Any], mesg: str = "") -> tuple[Any, int]:
        # FIX: DeleteMe
        item, keycode = self.prompt(
            items=list(items.values()),
            mesg=mesg,
            markup=self.client.markup,
        )
        name = helpers.extract_key_from_str(item, sep=SEPARATOR)
        try:
            selected = items[name]
        except KeyError as err:
            err_msg = f"item='{name}' not found"
            logger.error(err_msg)
            raise ValueError(err_msg) from err
        return selected, keycode

    def multi_selection(self, **kwargs) -> None:
        self.menu.keybind.toggle_all()
        items = kwargs.get("items", self.client.streams)
        mesg = f"> Showing ({len(items)}) items.\n>> Use 'Shift'+'Enter' for multi-select"
        selections, keycode = self.prompt(
            items=tuple(items.values()),
            mesg=mesg,
            multi_select=True,
            markup=self.client.markup,
        )

        if keycode == 1 or not selections:
            sys.exit(1)

        for item in selections:
            if not item.playable:
                logger.info(f"{item.name=} is offline.")
                continue
            self.play(item)
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

    def get_item(self, items: Mapping[str, Any], name: str) -> Any:
        # FIX: DeleteMe
        try:
            item = items[name]
        except KeyError as err:
            err_msg = f"item='{name}' not found"
            logger.error(err_msg)
            raise ValueError(err_msg) from err
        return item

    def play(self, follow) -> int:
        logger.warning(f"playing content {follow.url=}")
        process = self.player.play(follow)
        return process.returncode

    def get_key(self, keycode: int) -> Keybind:
        return self.menu.keybind.get_keybind_by_code(keycode)

    def chat(self, **kwargs) -> None:
        item = kwargs.pop("item")
        webbrowser.open_new_tab(item.chat)
        sys.exit(0)

    def close(self) -> None:
        logger.debug("closing connection")
        self.client.api.client.close()
