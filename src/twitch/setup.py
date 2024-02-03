# setup.py
from __future__ import annotations

import argparse
import functools
from typing import TYPE_CHECKING
from typing import Callable

from pyselector import Menu
from twitch.app import Keys
from twitch.app import TwitchApp

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

keys = Keys(
    quit="alt-q",
    channels="alt-a",
    categories="alt-t",
    videos="alt-v",
    chat="alt-o",
    information="alt-i",
    multi_selection="alt-m",
    show_all="alt-u",
    search_by_game="alt-s",
    search_by_query="alt-c",
)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video from twitch.",
    )

    markup_group = parser.add_argument_group(title="menu options")
    markup_group.add_argument("--no-markup", action="store_false", help="Disable pango markup")

    # experimental
    parser.add_argument("--channel", "-c", help="Search by channel query", action="store_true")
    parser.add_argument("--games", "-g", help="Search by game or category", action="store_true")

    # options
    parser.add_argument("-m", "--menu", choices=["rofi", "dmenu"], help="Select a launcher/menu", default="rofi")
    parser.add_argument("-p", "--player", default="mpv", choices=["streamlink", "mpv"])
    parser.add_argument("-t", "--test", action="store_true", help="Test mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    args = parser.parse_args()

    if args.menu in ["fzf", "dmenu"]:
        args.no_markup = False
    return args


def keybinds(twitch: TwitchApp) -> TwitchApp:
    twitch.menu.keybind.add(
        key=keys.channels,
        description="show channels",
        callback=twitch.show_all_streams,
    )
    twitch.menu.keybind.add(
        key=keys.categories,
        description="show by games",
        callback=twitch.show_categories,
    )
    twitch.menu.keybind.add(
        key=keys.videos,
        description="show videos",
        callback=twitch.show_channel_videos,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.chat,
        description="launch chat",
        callback=twitch.chat,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.information,
        description="display item info",
        callback=twitch.get_item_info,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.multi_selection,
        description="multiple selection",
        callback=twitch.multi_selection,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_game,
        description="search games or categories",
        callback=twitch.show_channels_by_game,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_query,
        description="search by channel",
        callback=twitch.show_channels_by_query,
    )
    twitch.menu.keybind.add(
        key=keys.show_all,
        description="show all keybinds",
        callback=twitch.show_keybinds,
    )
    twitch.menu.keybind.add(
        key=keys.quit,
        description="quit",
        callback=twitch.quit,
    )
    return twitch


def menu(args: argparse.Namespace) -> tuple[MenuInterface, Callable]:
    menu = Menu.get(args.menu)
    prompt = functools.partial(
        menu.prompt,
        prompt="Twitch>",
        lines=15,
        width="75%",
        height="60%",
        markup=args.no_markup,
        preview=False,
        # theme="catppuccin-macchiato",
        location="center",
    )
    return menu, prompt


def test(**kwargs) -> None:  # noqa: ARG001
    print("Testing mode, not launching menu")  # noqa: T201
