# setup.py
from __future__ import annotations

import argparse
import functools
import sys
import textwrap
from typing import TYPE_CHECKING

from pyselector import Menu
from twitch.api import TwitchApi
from twitch.app import Keys
from twitch.app import TwitchApp
from twitch.client import TwitchClient
from twitch.player import FactoryPlayer

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

# app
DESC = 'Simple tool menu for watching streams, videos from twitch.'
HELP = DESC
HELP += textwrap.dedent(
    """

options:
    -c, --channel   search by channel query
    -g, --games     search by game or category
    -m, --menu      select menu [rofi|dmenu] (default: rofi)
    -p, --player    select player [mpv|streamlink] (default: mpv)
    -v, --verbose   verbose mode
    -h, --help      show this help

menu options:
    --no-markup     disable pango markup
    """
)


keys = Keys(
    quit='alt-q',
    channels='alt-a',
    categories='alt-t',
    videos='alt-v',
    chat='alt-o',
    information='alt-i',
    multi_selection='alt-m',
    show_all='alt-u',
    search_by_game='alt-s',
    search_by_query='alt-c',
)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=HELP,
        description=DESC,
        add_help=False,
    )

    markup_group = parser.add_argument_group(title='menu options')
    markup_group.add_argument('--no-markup', action='store_false')

    # experimental
    parser.add_argument('--channel', '-c', action='store_true')
    parser.add_argument('--games', '-g', action='store_true')

    # options
    parser.add_argument('-m', '--menu', choices=['rofi', 'dmenu'], default='rofi')
    parser.add_argument('-p', '--player', default='mpv', choices=['streamlink', 'mpv'])
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-h', '--help', action='store_true')

    args = parser.parse_args()
    if args.menu in ['fzf', 'dmenu']:
        args.no_markup = False
    return args


def keybinds(twitch: TwitchApp) -> TwitchApp:
    twitch.menu.keybind.add(
        key=keys.channels,
        description='show channels',
        callback=twitch.show_all_streams,
    )
    twitch.menu.keybind.add(
        key=keys.categories,
        description='show by games',
        callback=twitch.show_categories,
    )
    twitch.menu.keybind.add(
        key=keys.videos,
        description='show videos',
        callback=twitch.show_channel_videos,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.chat,
        description='launch chat',
        callback=twitch.chat,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.information,
        description='display item info',
        callback=twitch.get_item_info,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.multi_selection,
        description='multiple selection',
        callback=twitch.multi_selection,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_game,
        description='search games or categories',
        callback=twitch.show_channels_by_game,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_query,
        description='search by channel',
        callback=twitch.show_channels_by_query,
    )
    twitch.menu.keybind.add(
        key=keys.show_all,
        description='show all keybinds',
        callback=twitch.show_keybinds,
    )
    twitch.menu.keybind.add(
        key=keys.quit,
        description='quit',
        callback=twitch.quit,
    )
    return twitch


def menu(args: argparse.Namespace) -> MenuInterface:
    menu = Menu.get(args.menu)
    menu.prompt = functools.partial(
        menu.prompt,
        prompt='Twitch>',
        lines=15,
        width='75%',
        height='60%',
        markup=args.no_markup,
        preview=False,
        location='center',
    )
    return menu


def test(**kwargs) -> None:  # noqa: ARG001
    print('Testing mode, not launching menu')
    sys.exit()


def app(menu: MenuInterface, player: str, markup: bool) -> TwitchApp:
    api = TwitchApi()
    client = TwitchClient(api, markup)
    return TwitchApp(client=client, menu=menu, player=FactoryPlayer.create(player))


def help() -> int:  # noqa: A001
    print(HELP)
    return 0
