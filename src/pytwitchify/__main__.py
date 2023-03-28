# main.py

from __future__ import annotations

import argparse
import functools
import logging
import sys

from . import app
from .twitch import TwitchClient
from .utils import logger


def main() -> int:
    """
    This function is the entry point of the program. It parses the command line arguments, initializes the TwitchClient
    and App objects, and starts the program by calling show_menu on the App object. If a KeyboardInterrupt exception
    is raised, the program terminates and prints a message to the console.
    """
    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video or clips from Twitch."
    )
    parser.add_argument("-m", "--menu", choices=["rofi", "dmenu", "fzf"], help="Select a launcher/menu", default="rofi")
    parser.add_argument("--lines", required=False, help="Show menu lines (default: 15)", nargs="?", default=15)
    parser.add_argument("-p", "--player", default="streamlink", choices=["streamlink", "mpv"])
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--test", help="", action="store_true")
    args = parser.parse_args()

    logger.set_logging_level(args.verbose)

    menu = app.get_launcher(args.menu)
    client = TwitchClient()

    prompt = functools.partial(
        menu.prompt,
        prompt="twitch>",
        lines=args.lines,
        width="55%",
        height="50%",
        mesg="Welcome to RofiTwitch",
        preview=False,
    )

    menu.keybind.add(
        key="alt-l",
        description="for only live",
        callback=app.display_live_follows,
    )
    menu.keybind.add(
        key="alt-a",
        description="for all follows",
        callback=app.display_all_follows,
    )
    menu.keybind.add(
        key="alt-i",
        description="for follow information",
        callback=app.display_follow_info,
    )

    try:
        channel = app.display_live_follows(client, prompt, menu)
        app.load_stream(args.player, channel)
    except KeyboardInterrupt:
        logging.info("Terminated by user.")
        sys.exit(0)
    finally:
        client.api.client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
