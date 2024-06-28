# setup.py
from __future__ import annotations

import argparse
import functools
import logging
import sys
from typing import TYPE_CHECKING

from pyselector import Menu
from twitch import constants
from twitch import player
from twitch.api import Credentials
from twitch.api import TwitchApi
from twitch.app import Keys
from twitch.app import TwitchApp
from twitch.client import TwitchFetcher

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

log = logging.getLogger(__name__)


keys = Keys(
    categories='alt-t',
    channels='alt-a',
    chat='alt-o',
    clips='alt-C',
    information='alt-i',
    search_by_game='alt-s',
    search_by_query='alt-c',
    show_all='alt-u',
    show_keys='alt-k',
    top_streams='alt-m',
    videos='alt-v',
    top_games='alt-g',
)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=constants.HELP,
        description=constants.DESC,
        add_help=False,
    )

    opts_group = parser.add_argument_group(title='options')
    opts_group.add_argument('--no-markup', action='store_false')
    opts_group.add_argument('-p', '--no-conf', action='store_false')

    # options
    parser.add_argument('-m', '--menu', choices=['rofi', 'dmenu'], default='rofi')
    parser.add_argument('-c', '--config', type=str)
    parser.add_argument('-C', '--channel', action='store_true')
    parser.add_argument('-G', '--games', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')

    args = parser.parse_args()
    if args.menu in ['fzf', 'dmenu']:
        args.no_markup = False
    return args


def keybinds(t: TwitchApp) -> TwitchApp:
    key = t.menu.keybind
    key.add(key=keys.channels, callback=t.show_all_streams, hidden=True, description='show channels')
    key.add(key=keys.categories, callback=t.show_by_categories, hidden=True, description='show by games')
    key.add(key=keys.videos, callback=t.show_videos, hidden=True, description='show videos')
    key.add(key=keys.clips, callback=t.show_clips, hidden=True, description='show clips')
    key.add(key=keys.chat, callback=t.open_chat, hidden=True, description='launch chat')
    key.add(key=keys.information, callback=t.show_item_info, hidden=True, description='display item info')
    key.add(key=keys.search_by_game, callback=t.show_by_game, hidden=True, description='search games')
    key.add(key=keys.search_by_query, callback=t.show_by_query, hidden=True, description='search by channel')
    key.add(key=keys.show_keys, callback=t.show_keybinds, hidden=False, description='show available keybinds')
    key.add(key=keys.top_streams, callback=t.show_top_streams, hidden=True, description='show top streams')
    key.add(key=keys.top_games, callback=t.show_top_games, hidden=True, description='show top games')
    return t


def menu(args: argparse.Namespace) -> MenuInterface:
    menu = Menu.get(args.menu)
    menu.prompt = functools.partial(
        menu.prompt,
        prompt='Twitch>',
        lines=15,
        width='75%',
        height='60%',
        markup=args.no_markup,
        location='center',
    )
    return menu


async def test(**kwargs) -> None:  # noqa: ARG001
    print('Testing mode, not launching menu')
    sys.exit()


async def app(menu: MenuInterface, args: argparse.Namespace) -> TwitchApp:
    credentials = Credentials.load(args.config)
    credentials.validate()
    api = TwitchApi(credentials)
    await api.load_client()
    fetcher = TwitchFetcher(api, args.no_markup)
    return TwitchApp(
        fetcher=fetcher,
        menu=menu,
        player=player.get(with_config=args.no_conf),
        keys=keys,
    )


def help() -> int:  # noqa: A001
    print(constants.HELP)
    return 0
