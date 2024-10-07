# setup.py
from __future__ import annotations

import argparse
import functools
import logging
from typing import TYPE_CHECKING
from typing import Any

from pyselector import Menu

from twitch import config
from twitch import constants
from twitch.api import Credentials
from twitch.api import TwitchApi
from twitch.app import TwitchApp
from twitch.client import TwitchFetcher

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

log = logging.getLogger(__name__)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=constants.HELP,
        description=constants.DESC,
        add_help=False,
    )

    opts_group = parser.add_argument_group(title='options')
    opts_group.add_argument('--no-markup', action='store_false')
    opts_group.add_argument('--no-ansi', action='store_false')
    opts_group.add_argument('--no-conf', action='store_false')

    # options
    parser.add_argument('-m', '--menu', choices=['rofi', 'dmenu', 'fzf'], default='rofi')
    parser.add_argument('-e', '--env', type=str)
    parser.add_argument('-C', '--channel', action='store_true')
    parser.add_argument('-G', '--games', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')

    args = parser.parse_args()
    if args.menu in ['fzf', 'dmenu']:
        args.no_markup = False
    if args.menu in ['dmenu', 'rofi']:
        args.no_ansi = False
    return args


def keybinds(t: TwitchApp) -> TwitchApp:
    keys = config.get_keybinds(constants.CONFIGFILE, constants.DEFAULT_KEYBINDS)
    keymap = t.menu.keybind
    keymap.add(bind=keys.group_by_cat, action=t.show_group_by_cat, hidden=True, description='show by games')
    keymap.add(bind=keys.show_information, action=t.show_item_info, hidden=True, description='display item info')
    keymap.add(bind=keys.open_chat, action=t.open_chat, hidden=True, description='launch chat')
    keymap.add(bind=keys.show_keys, action=t.show_keybinds, hidden=False, description='show available keybinds')
    keymap.add(bind=keys.search_by_game, action=t.show_by_game, hidden=True, description='search game by query')
    keymap.add(bind=keys.search_by_query, action=t.show_by_query, hidden=True, description='search channel by query')
    keymap.add(bind=keys.multiselection, action=t.multi_selection, hidden=True, description='enable multiselection')
    # Content
    keymap.add(bind=keys.top_streams, action=t.show_top_streams, hidden=True, description='show top streams')
    keymap.add(bind=keys.top_games, action=t.show_top_games, hidden=True, description='show top games')
    keymap.add(bind=keys.videos, action=t.show_videos, hidden=True, description='show videos')
    keymap.add(bind=keys.clips, action=t.show_clips, hidden=True, description='show clips')
    return t


def menu(args: argparse.Namespace) -> MenuInterface:
    menu = Menu.get(args.menu)
    menu.select = functools.partial(
        menu.select,
        prompt='Twitch> ',
        lines=15,
        width='85%',
        height='60%',
        markup=args.no_markup,
        ansi=args.no_ansi,
        location='center',
    )
    return menu


async def test(**kwargs: Any) -> int:  # noqa: ARG001
    print('Testing mode, not launching menu')
    return 0


async def app(menu: MenuInterface, args: argparse.Namespace) -> TwitchApp:
    credentials = Credentials.load(args.env)
    credentials.validate()
    api = TwitchApi(credentials)
    fetcher = TwitchFetcher(api)
    await fetcher.api.load_client()
    return TwitchApp(
        fetcher=fetcher,
        menu=menu,
        player_conf=args.no_conf,
        keys=config.get_keybinds(constants.CONFIGFILE, constants.DEFAULT_KEYBINDS),
        markup=args.no_markup,
        ansi=args.no_ansi,
    )


def help() -> None:  # noqa: A001
    print(constants.HELP)
