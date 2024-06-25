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


class TwitchPlayableContent(typing.Protocol):
    url: str


def mpv_logger(*args, prefix: str) -> None:
    message = args[2].rstrip('\n')
    result = f'{prefix}: {message}'
    log.error(result)


def get(with_config: bool = False, name: str = __appname__) -> mpv.MPV:
    p = mpv.MPV(
        config=with_config,
        log_handler=partial(mpv_logger, prefix=name),
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        ytdl=True,
    )
    p.set_loglevel('error')

    @p.on_key_press('q')
    def my_q_binding():
        p.quit(0)

    return p
