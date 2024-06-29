# player.py
from __future__ import annotations

import logging
import typing
from functools import partial

import mpv
from twitch.__about__ import __appname__

log = logging.getLogger(__name__)

# TODO:
# - [ ] multiple instances: https://github.com/jaseg/python-mpv/issues/126


def get_current_logging_level() -> tuple[str, typing.Callable]:
    logging_level = {
        10: ('debug', log.debug),
        20: ('info', log.info),
        30: ('warn', log.warn),
        40: ('error', log.error),
    }
    return logging_level[logging.root.level]


def mpv_logger(*args, prefix: str, logger: typing.Callable) -> None:
    message = args[2].rstrip('\n')
    result = f'{prefix}: {message}'
    logger(result)


def get(with_config: bool = False, name: str = __appname__) -> mpv.MPV:
    level, log_fn = get_current_logging_level()
    p = mpv.MPV(
        config=with_config,
        log_handler=partial(mpv_logger, prefix=f'[{name}]', logger=log_fn),
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        ytdl=True,
    )
    p.set_loglevel(level)

    @p.on_key_press('q')
    def my_q_binding():
        p.quit(0)

    return p
