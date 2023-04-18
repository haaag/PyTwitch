from __future__ import annotations

import argparse
import functools
import logging
import sys

from src.twitch import helpers
from src.twitch import logger
from src.twitch.app import App
from src.twitch.app import Keys
from src.twitch.client import TwitchClient
from src.twitch.player import create_player

keys = Keys(
    channels="alt-a",
    categories="alt-t",
    clips="alt-c",
    videos="alt-v",
    chat="alt-o",
)


def main() -> int:
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
    # player.add_options("--no-border --no-keepaspect-window")

    prompt = functools.partial(
        menu.prompt,
        prompt="Twitch>",
        lines=args.lines,
        width="65%",
        height="60%",
        markup=args.no_markup,
        preview=False,
        theme="dracula",
    )

    twitch = App(client, prompt, menu, player, keys)
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

    try:
        item = twitch.run()
        twitch.play(item)
        # twitch.record(item, path="~/dev/python/twitch")
    except KeyboardInterrupt:
        log.info("Terminated by user")
    finally:
        client.api.client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
