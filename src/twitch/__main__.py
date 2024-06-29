from __future__ import annotations

import asyncio
import logging
import sys

from twitch import logger
from twitch import setup
from twitch._exceptions import CONNECTION_EXCEPTION
from twitch._exceptions import EXCEPTIONS

# TODO)):
# - [X] ~~Read https://dev.twitch.tv/docs/api/reference/#get-games~~

VERBOSE_ON = 3


def main() -> int:
    args = setup.args()
    logger.verbose(args.verbose)
    log = logging.getLogger(__name__)

    if args.verbose:
        log.debug('arguments: %s', vars(args))

    if args.help:
        return setup.help()

    menu = setup.menu(args)
    try:
        asverbose = args.verbose == VERBOSE_ON
        run = asyncio.run
        twitch = run(setup.app(menu, args))
        twitch = setup.keybinds(twitch)

        if args.test:
            run(setup.test(t=twitch), debug=asverbose)
        if args.channel:
            run(twitch.show_by_query(), debug=asverbose)
        elif args.games:
            run(twitch.show_by_game(), debug=asverbose)
        else:
            run(twitch.show_all_streams(), debug=asverbose)
    except (*CONNECTION_EXCEPTION, *EXCEPTIONS) as err:
        menu.keybind.unregister_all()
        menu.prompt(items=[f'{err!r}'], markup=False, prompt='PyTwitchErr>')
        log.error(err)
    except KeyboardInterrupt:
        log.info('terminated by user')
    return 0


if __name__ == '__main__':
    sys.exit(main())
