# setup.py
from __future__ import annotations

import argparse
import functools
import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from pyselector import Menu
from twitch import constants
from twitch import player
from twitch._exceptions import EnvValidationError
from twitch.api import Credentials
from twitch.api import TwitchApi
from twitch.app import Keys
from twitch.app import TwitchApp
from twitch.client import TwitchClient

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

log = logging.getLogger(__name__)


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
    show_keys='alt-k',
)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=constants.HELP,
        description=constants.DESC,
        add_help=False,
    )

    markup_group = parser.add_argument_group(title='menu options')
    markup_group.add_argument('--no-markup', action='store_false')

    # experimental
    parser.add_argument('-C', '--channel', action='store_true')
    parser.add_argument('-G', '--games', action='store_true')

    # options
    parser.add_argument('-m', '--menu', choices=['rofi', 'dmenu'], default='rofi')
    # parser.add_argument('-p', '--player', default='mpv', choices=['mpv'])
    # parser.add_argument('-a', '--player-args', type=str)
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--config', type=str)
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
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.categories,
        description='show by games',
        callback=twitch.show_categories,
        hidden=True,
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
    # twitch.menu.keybind.add(
    #     key=keys.multi_selection,
    #     description='multiple selection',
    #     callback=twitch.multi_selection,
    #     hidden=True,
    # )
    twitch.menu.keybind.add(
        key=keys.search_by_game,
        description='search games or categories',
        callback=twitch.show_channels_by_game,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_query,
        description='search by channel',
        callback=twitch.show_channels_by_query,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.show_all,
        description='show all keybinds',
        callback=twitch.show_keybinds,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.quit,
        description='quit',
        callback=twitch.quit,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.show_keys,
        description='show available keybinds',
        callback=twitch.show_keybinds,
        hidden=False,
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


def load_credentials(file: str) -> Credentials:
    if file:
        read_env_file(file)
    else:
        load_dotenv()
    access_token = os.environ.get('TWITCH_ACCESS_TOKEN')
    cliend_id = os.environ.get('TWITCH_CLIENT_ID')
    user_id = os.environ.get('TWITCH_USER_ID')
    return Credentials(
        access_token=access_token,
        client_id=cliend_id,
        user_id=user_id,
    )


def app(menu: MenuInterface, args: argparse.Namespace) -> TwitchApp:
    credentials = load_credentials(args.config)
    credentials.validate()
    api = TwitchApi(credentials)
    api.load_client()
    client = TwitchClient(api, args.no_markup)
    return TwitchApp(client=client, menu=menu, player=player.get_player())


def help() -> int:  # noqa: A001
    print(constants.HELP)
    return 0


def read_env_file(path: str | None = None) -> None:
    """Load envs if path"""
    if not path:
        return
    fullpath = Path().absolute() / Path(path)
    if not fullpath.exists():
        err = f'{fullpath=!s} not found'
        log.error(err)
        raise EnvValidationError(err)
    if not fullpath.is_file():
        err = f'{fullpath=!s} is not a file'
        log.error(err)
        raise EnvValidationError(err)

    log.debug(f'loading envs from {fullpath=!s}')
    load_dotenv(dotenv_path=fullpath.as_posix())
