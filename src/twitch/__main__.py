from __future__ import annotations

import argparse
import functools
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Callable

from pyselector import Menu

from src.twitch import logger
from src.twitch._exceptions import CONNECTION_EXCEPTION
from src.twitch._exceptions import EXCEPTIONS
from src.twitch.app import Keys
from src.twitch.app import TwitchApp
from src.twitch.client import TwitchClient
from src.twitch.player import FactoryPlayer

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

keys = Keys(
    channels="alt-a",
    categories="alt-t",
    clips="alt-c",
    videos="alt-v",
    chat="alt-o",
    information="alt-i",
)


def _set_keybinds(twitch: TwitchApp, args: argparse.Namespace) -> TwitchApp:
    twitch.menu.keybind.add(
        key=args.channels,
        description="show channels",
        callback=twitch.get_channels_and_streams,
    )
    twitch.menu.keybind.add(
        key=args.categories,
        description="show by games",
        callback=twitch.show_categories,
    )
    twitch.menu.keybind.add(
        key=args.clips,
        description="show clips",
        callback=twitch.get_channel_clips,
    )
    twitch.menu.keybind.add(
        key=args.videos,
        description="show videos",
        callback=twitch.get_channel_videos,
    )
    twitch.menu.keybind.add(
        key=args.chat,
        description="launch chat",
        callback=twitch.chat,
    )
    twitch.menu.keybind.add(
        key=keys.information,
        description="display item info",
        callback=twitch.get_item_info,
    )
    return twitch


def _setup_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video or clips from src.twitch.",
    )

    markup_group = parser.add_argument_group(title="menu options")
    markup_group.add_argument("--no-markup", action="store_false", help="Disable pango markup")

    # keybinds
    parser.add_argument("--channels", help="Show all channels", default=keys.channels)
    parser.add_argument("--categories", help="Show all categories or games", default=keys.categories)
    parser.add_argument("--clips", help="Show all clips of the selected channel", default=keys.clips)
    parser.add_argument("--videos", help="Show all videos of the selected channel", default=keys.videos)
    parser.add_argument("--chat", help="Open the chat of the selected stream", default=keys.chat)

    # options
    parser.add_argument(
        "-m", "--menu", choices=["rofi", "dmenu", "fzf", "rofi_beta"], help="Select a launcher/menu", default="rofi"
    )
    parser.add_argument("-l", "--lines", help="Show menu lines (default: 15)", nargs="?", default=15)
    parser.add_argument("-p", "--player", default="mpv", choices=["streamlink", "mpv"])
    parser.add_argument("-t", "--test", action="store_true", help="Test mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    args = parser.parse_args()

    if args.menu in ["fzf", "dmenu"]:
        args.no_markup = False
    return args


def _setup_menu(args: argparse.Namespace) -> tuple[MenuInterface, Callable]:
    menu = Menu.get(args.menu)
    prompt = functools.partial(
        menu.prompt,
        prompt="Twitch>",
        lines=args.lines,
        width="65%",
        height="60%",
        markup=args.no_markup,
        preview=False,
        theme="gruvbox-new",
        location="center",
    )
    return menu, prompt


def main() -> int:
    args = _setup_args()

    logger.verbose(args.verbose)
    log = logging.getLogger(__name__)

    if args.verbose:
        log.info("arguments: %s", vars(args))

    menu, prompt = _setup_menu(args)

    try:
        twitch = TwitchApp(
            client=TwitchClient(markup=args.no_markup),
            prompt=prompt,
            menu=menu,
            player=FactoryPlayer.create(args.player),
            keys=keys,
        )
        twitch = _set_keybinds(twitch, args)

        item = twitch.run_loop()
        twitch.play(item)
        twitch.close()
    except EXCEPTIONS as err:
        prompt(items=[f"{err!r}"])
    except CONNECTION_EXCEPTION as err:
        prompt(items=[f"{err!r}"], markup=False)
        log.error(err)
    except KeyboardInterrupt:
        log.info("Terminated by user")
    return 0


if __name__ == "__main__":
    sys.exit(main())
