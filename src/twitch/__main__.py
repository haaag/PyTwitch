from __future__ import annotations

import logging
import sys

from twitch import logger
from twitch import setup
from twitch._exceptions import CONNECTION_EXCEPTION
from twitch._exceptions import EXCEPTIONS
from twitch.api import TwitchApi
from twitch.app import TwitchApp
from twitch.client import TwitchClient
from twitch.player import FactoryPlayer

# TODO:
# Read https://dev.twitch.tv/docs/api/reference/#get-games


def main() -> int:
    args = setup.args()
    logger.verbose(args.verbose)
    log = logging.getLogger(__name__)

    if args.verbose:
        log.info('arguments: %s', vars(args))

    try:
        menu, prompt = setup.menu(args)
        api = TwitchApi()
        api.validate_credentials()
        twitch = TwitchApp(
            client=TwitchClient(api=api, markup=args.no_markup),
            prompt=prompt,
            menu=menu,
            player=FactoryPlayer.create(args.player),
        )
        twitch = setup.keybinds(twitch)

        if args.test:
            setup.test()
            sys.exit()

        if args.channel:
            twitch.show_channels_by_query()
        elif args.games:
            twitch.show_channels_by_game()
        else:
            twitch.show_all_streams()
        twitch.close()
    except EXCEPTIONS as err:
        prompt(items=[f'{err!r}'])
        log.error(err)
    except CONNECTION_EXCEPTION as err:
        prompt(items=[f'{err!r}'], markup=False)
        log.error(err)
    except KeyboardInterrupt:
        log.info('terminated by user')
    return 0


if __name__ == '__main__':
    sys.exit(main())
