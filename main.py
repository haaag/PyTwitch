# main.py

import argparse
import sys

from twitch.app import App
from twitch.twitch import TwitchClient
from twitch.utils import logger
from twitch.utils.menu import get_menu


def main() -> None:
    """
    This function is the entry point of the program. It parses the command line arguments, initializes the TwitchClient
    and App objects, and starts the program by calling show_menu on the App object. If a KeyboardInterrupt exception
    is raised, the program terminates and prints a message to the console.
    """

    parser = argparse.ArgumentParser(
        description="Simple tool menu for watching streams live, video or clips from Twitch."
    )
    parser.add_argument("--rofi", "-r", action="store_true", help="Set launcher to Rofi (default: dmenu)")
    parser.add_argument(
        "--lines", type=int, required=False, help="Show dmenu in lines (default: 12 lines)", nargs="?", default=12
    )
    parser.add_argument("--player", type=str, required=False, help="Player (default: mpv)", nargs="?", default="mpv")
    parser.add_argument("-l", "--live", action="store_true", help="Show only live streams only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--test", help="", action="store_true")
    args = parser.parse_args()

    logger.set_logging_level(args.verbose)

    twitch = TwitchClient()
    menu = get_menu(rofi=args.rofi, lines=args.lines)
    app = App(twitch=twitch, menu=menu, player=args.player)

    try:
        if args.test:
            sys.exit(0)

        if args.live:
            app.show_online_follows()
            sys.exit(0)

        app.show_follows_and_online()
    except KeyboardInterrupt:
        print("Terminated by user.")
        sys.exit(0)
    finally:
        app.twitch.api.client.close()


if __name__ == "__main__":
    main()
