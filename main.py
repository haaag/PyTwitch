# main.py

import argparse
import logging
import sys

from twitch.app import App
from twitch.twitch import TwitchClient
from twitch.utils import logger
from twitch.utils.menu import get_menu


def main() -> None:
    """
    main

    This function is the entry point of the program. It parses the command line arguments, initializes the TwitchClient
    and App objects, and starts the program by calling show_menu on the App object. If a KeyboardInterrupt exception
    is raised, the program terminates and prints a message to the console.

    Args:
    --rofi (bool): Set launcher to Rofi (default: dmenu)
    --lines (int): Show dmenu in lines (default: 12)
    --player (str): Specify player to use to play streams (default: mpv)
    --bottom (bool): Show dmenu bottom
    """
    logger.set_logging_level(logging.INFO)

    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video or clips from Twitch."
    )
    parser.add_argument("--rofi", action="store_true", help="Set launcher to Rofi (default: dmenu)")
    parser.add_argument("--lines", type=int, required=False, help="Show dmenu in lines", nargs="?", const=12)
    parser.add_argument("--player", type=str, required=False, help="Show dmenu in lines", nargs="?", default="mpv")
    parser.add_argument("--bottom", action="store_true", help="Show dmenu bottom")
    parser.add_argument("--mixed", action="store_true", help="All channels, live with live icon.")
    parser.add_argument("--live", action="store_true", help="Show only live streams")
    parser.add_argument("--test", help="", action="store_true")
    args = parser.parse_args()

    twitch = TwitchClient()
    menu = get_menu(rofi=args.rofi, lines=args.lines, bottom=args.bottom)
    app = App(twitch=twitch, menu=menu, player=args.player)

    if args.test:
        app.show_follows()
        sys.exit(0)

    if args.mixed:
        app.show_follows_and_online()
        sys.exit(0)

    if args.live:
        app.show_online_follows()
        sys.exit(0)

    app.show_menu()
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Terminated by user.")
        sys.exit(1)
