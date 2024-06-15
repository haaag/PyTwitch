from __future__ import annotations

import logging
import sys

from twitch import logger
from twitch import setup
from twitch._exceptions import CONNECTION_EXCEPTION
from twitch._exceptions import EXCEPTIONS

# TODO:
# Read https://dev.twitch.tv/docs/api/reference/#get-games


def main() -> int:
    args = setup.args()
    logger.verbose(args.verbose)
    log = logging.getLogger(__name__)

    if args.verbose:
        log.info('arguments: %s', vars(args))

    menu = setup.menu(args)

    try:
        twitch = setup.app(menu, args)
        twitch = setup.keybinds(twitch)

        if args.test:
            setup.test()
        if args.help:
            return setup.help()
        if args.channel:
            twitch.show_channels_by_query()
        elif args.games:
            twitch.show_channels_by_game()
        else:
            twitch.show_all_streams()
        twitch.quit(keycode=0)
    except (*CONNECTION_EXCEPTION, *EXCEPTIONS) as err:
        menu.prompt(items=[f'{err!r}'], markup=False)
    except KeyboardInterrupt:
        log.info('terminated by user')
    return 0


if __name__ == '__main__':
    sys.exit(main())
