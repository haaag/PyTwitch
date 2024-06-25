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
    categories='alt-t',
    channels='alt-a',
    chat='alt-o',
    clips='alt-C',
    information='alt-i',
    quit='alt-q',
    search_by_game='alt-s',
    search_by_query='alt-c',
    show_all='alt-u',
    show_keys='alt-k',
    top_streams='alt-m',
    videos='alt-v',
    # multi_selection='alt-m',
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
        callback=twitch.show_videos,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.clips,
        description='show clips',
        callback=twitch.show_clips,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.chat,
        description='launch chat',
        callback=twitch.open_chat,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.information,
        description='display item info',
        callback=twitch.show_item_info,
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
        callback=twitch.show_by_game,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.search_by_query,
        description='search by channel',
        callback=twitch.show_by_query,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.show_all,
        description='show all keybinds',
        callback=twitch.show_keybinds,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.show_keys,
        description='show available keybinds',
        callback=twitch.show_keybinds,
        hidden=False,
    )
    twitch.menu.keybind.add(
        key=keys.top_streams,
        description='show top streams',
        callback=twitch.show_top_streams,
        hidden=True,
    )
    twitch.menu.keybind.add(
        key=keys.quit,
        description='quit',
        callback=twitch.quit,
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
    load_envs(file)
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
    return TwitchApp(
        client=client,
        menu=menu,
        player=player.get(with_config=args.no_conf),
        keys=keys,
    )


def help() -> int:  # noqa: A001
    print(constants.HELP)
    return 0


def load_envs(filepath: str | None = None) -> None:
    """Load envs if path"""
    if not filepath:
        log.info('env: no env filepath specified')
        log.info('env: loading from .env or exported env vars')
        load_dotenv()
        return

    envfilepath = Path().absolute() / Path(filepath)
    if not envfilepath.exists():
        err = f'{envfilepath=!s} not found'
        raise EnvValidationError(err)
    if not envfilepath.is_file():
        err = f'{envfilepath=!s} is not a file'
        raise EnvValidationError(err)

    log.info(f'env: loading envs from {envfilepath=!s}')
    load_dotenv(dotenv_path=envfilepath.as_posix())
