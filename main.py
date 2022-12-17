# main.py

import argparse
import logging
import sys

from twitch.app import App
from twitch.twitch import TwitchClient
from twitch.utils import logger
from twitch.utils.menu import get_launcher


def main() -> None:
    logger.set_logging_level(logging.INFO)

    parser = argparse.ArgumentParser(description="Tool from Twitch")
    parser.add_argument("--rofi", action="store_true", help="Set launcher to Rofi (default: dmenu)")
    parser.add_argument("--lines", type=int, required=False, help="Show dmenu in lines", default=15)
    parser.add_argument("--bottom", action="store_true", help="Show dmenu in lines")
    parser.add_argument("--test", help="", action="store_true")
    parser.add_argument("--test-other", help="", action="store_true")

    args = parser.parse_args()

    launcher = get_launcher(args.rofi, lines=args.lines, bottom=args.bottom)
    app = App(twitch=TwitchClient(), menu=launcher)

    app.show_menu()
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Terminated by user.")
