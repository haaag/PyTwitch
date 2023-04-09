# app.py

from __future__ import annotations

import json
import logging
import re
import typing
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Union

from pytwitchify import helpers

if typing.TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

    from pytwitchify.client import TwitchClient
    from pytwitchify.datatypes import TwitchChannel
    from pytwitchify.datatypes import TwitchPlayableContent
    from pytwitchify.follows import Category
    from pytwitchify.follows import FollowedChannelInfo
    from pytwitchify.player import Player

log = logging.getLogger(__name__)


class App:
    follow: TwitchPlayableContent
    keycode: int
    follows: Mapping[str, TwitchChannel]

    def __init__(self, client: TwitchClient, prompt: Callable, menu: MenuInterface, player: Player):
        self.client = client
        self.prompt = prompt
        self.menu = menu
        self.player = player

    def handle_input(self) -> Union[TwitchPlayableContent, int]:
        log.info(f"{self.keycode=}")

        for keybind in self.menu.keybind.registered_keys:
            if keybind.code == self.keycode:
                return keybind.callback()

        if hasattr(self.follow, "live") and self.follow.live:
            return self.play(self.follow)

        return self.display_follow_videos()

    def display_follows(self, **kwargs) -> TwitchPlayableContent:
        self.follows = self.client.follows_merged()
        follows_to_show = [follow.stringify(self.client.markup) for follow in self.follows.values()]
        selected, self.keycode = self.prompt(
            items=follows_to_show,
            mesg=f"> Showing ({len(self.follows)}) channels",
        )

        username = helpers.extract_str_from_span(selected)
        self.follow = self.follows[username]
        return self.handle_input()

    def display(self, items: Mapping[str, TwitchPlayableContent]) -> TwitchPlayableContent:
        # FIX: Make a generic method that takes items and mesg for self.prompt
        to_show = [item.stringify(self.client.markup) for item in items.values()]
        selected, self.keycode = self.prompt(
            items=to_show,
            mesg=f"> Showing ({len(to_show)}) channels",
        )

        if self.keycode != 0:
            self.handle_input()

        username = helpers.extract_str_from_span(selected)
        self.follow = items[username]
        return self.follow

    def display_follow_videos(self) -> int:
        self.menu.keybind.unregister_all()
        videos = list(self.client.channels.content.get_videos(self.follow.user_id))

        if len(videos) == 0:
            mesg = f"No videos found for {self.follow.name}"
            self.prompt([mesg])
            log.error(mesg)
            raise SystemExit(1)

        item, keycode = self.prompt(
            items=[f"{i}:::{item.stringify(self.client.markup)}" for i, item in enumerate(videos)],
            mesg=f"> Showing ({len(videos)}) videos from channel <{self.follow.name}>",
        )

        try:
            idx = helpers.extract_id_from_str(item, sep=":")
        except ValueError as err:
            raise SystemExit(f"{item=} not found") from err
        return self.play(videos[idx])

    def display_follow_clips(self) -> int:
        self.menu.keybind.unregister_all()
        clips = self.client.get_follow_clips(self.follow.user_id)

        if len(clips) == 0:
            mesg = f"No clips found for {self.follow.name}"
            self.prompt([mesg])
            log.error(mesg)
            raise SystemExit(1)

        item, keycode = self.prompt(
            items=list(clips),
            mesg=f"> Showing ({len(clips)}) clips from channel <{self.follow.name}>",
        )

        try:
            idx = helpers.extract_id_from_str(item, sep=":")
        except ValueError as err:
            raise SystemExit(f"{item=} not found") from err

        return self.play(list(clips.values())[idx])

    def display_categories(self) -> Union[TwitchPlayableContent, int]:
        self.menu.keybind.toggle_hidden()
        categories = self.client.follows_categorized()
        categories_and_len = [f"{c} ({len(categories[c])})" for c in categories]

        category_selected, _ = self.prompt(
            items=categories_and_len,
            mesg=f"> Showing ({len(categories_and_len)}) categories",
            markup=False,
        )

        if category_selected not in categories_and_len:
            raise ValueError(f"{category_selected=} not found")

        category = re.sub(r"\s*\(\d+\)", "", category_selected)

        log.error(type(categories[category]))
        log.error(categories[category])

        follows: list[FollowedChannelInfo] = []
        for follow_dict in categories[category]:
            for follow in follow_dict.values():
                follows.append(follow)

        return self.display_follows_by_category(follows)

    def display_follows_by_category(
        self, follows_by_category: list[FollowedChannelInfo]
    ) -> Union[TwitchPlayableContent, int]:
        # FIX: Split it...
        self.menu.keybind.toggle_hidden(restore=True)
        online = {}
        follows_offline = {follow.name: follow for follow in follows_by_category}
        follows_online = self.client.channels.get_channels_live

        for live in follows_online:
            if live.name in follows_offline:
                follows_offline.pop(live.name)
                online[live.name] = live
        final_follows: Mapping[str, TwitchPlayableContent] = dict(online, **follows_offline)
        follows_to_show = [follow.stringify(self.client.markup) for follow in final_follows.values()]

        self.selected, self.keycode = self.prompt(
            items=follows_to_show,
            mesg=f"> Showing ({len(final_follows)}) channels",
        )

        username = helpers.extract_str_from_span(self.selected)
        self.follow = final_follows[username]
        return self.handle_input()

    def play(self, follow: TwitchPlayableContent) -> int:
        log.warning(f"playing content {follow=}")
        return self.player.play(follow)

    def run(self) -> None:
        self.display_follows()

    def json(self, data: Mapping[str, Any]) -> None:
        json_output = json.dumps([obj.__dict__ for obj in data])
        print(json_output)

    def display_by_categories(self) -> Category:
        self.menu.keybind.toggle_hidden()
        data = {str(c): c for c in self.client.follows_categorized_beta()}
        show = list(data)

        item, keycode = self.prompt(
            items=show,
            markup=True,
        )

        log.warning(item)
        category = item.split("<")[0].strip()
        log.error(f"{category=}")

        return self.display_items(data[item])

    def display_items(self, category: Category) -> None:
        self.menu.keybind.toggle_hidden(restore=True)
        item, self.keycode = self.prompt(
            items=[item.stringify(self.client.markup) for item in category.channels],
            markup=True,
        )
        username = helpers.extract_str_from_span(item)
        for channel in category.channels:
            if channel.name == username:
                self.follow = channel
        self.handle_input()
