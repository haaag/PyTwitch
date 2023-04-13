# main.py

from __future__ import annotations

import argparse
import functools
import logging

from pytwitchify import helpers
from pytwitchify import logger
from pytwitchify.app import App
from pytwitchify.app import Keys
from pytwitchify.client import TwitchClient
from pytwitchify.player import create_player

keys = Keys(
    channels="alt-a",
    categories="alt-t",
    clips="alt-c",
    videos="alt-v",
    chat="alt-o",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video or clips from Twitch.",
    )

    markup_group = parser.add_argument_group(title="menu options")
    markup_group.add_argument("--no-markup", action="store_false", help="Disable pango markup")

    parser.add_argument("-m", "--menu", choices=["rofi", "dmenu", "fzf"], help="Select a launcher/menu", default="rofi")
    parser.add_argument("-l", "--lines", help="Show menu lines (default: 15)", nargs="?", default=15)
    parser.add_argument("-p", "--player", default="mpv", choices=["streamlink", "mpv"])
    parser.add_argument("-t", "--test", action="store_true", help="Test mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    logger.verbose(args.debug)
    log = logging.getLogger(__name__)

    if args.debug:
        log.info("arguments: %s", vars(args))

    if args.menu in ["fzf", "dmenu"]:
        args.no_markup = False

    menu = helpers.get_launcher(args.menu)
    client = TwitchClient(markup=args.no_markup)
    player = create_player(args.player)

    prompt = functools.partial(
        menu.prompt,
        prompt="Twitch>",
        lines=args.lines,
        width="65%",
        height="60%",
        markup=args.no_markup,
        preview=False,
    )

    twitch = App(client, prompt, menu, player, keys)
    twitch.menu.keybind.add(
        key="alt-a",
        description="show channels",
        callback=twitch.get_channels_and_streams,
    )
    twitch.menu.keybind.add(
        key="alt-t",
        description="show by games",
        callback=twitch.show_categories,
    )
    twitch.menu.keybind.add(
        key="alt-c",
        description="show clips",
        callback=twitch.get_channel_clips,
    )
    twitch.menu.keybind.add(
        key="alt-v",
        description="show videos",
        callback=twitch.get_channel_videos,
    )
    twitch.menu.keybind.add(
        key=keys.chat,
        description="launch chat",
        callback=twitch.chat,
    )

    try:
        item = twitch.run()
        twitch.play(item)
    except KeyboardInterrupt:
        log.info("Terminated by user")
    finally:
        client.api.client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
