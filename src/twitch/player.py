# player.py
from __future__ import annotations

import logging
import typing

import mpv

log = logging.getLogger(__name__)


class TwitchPlayableContent(typing.Protocol):
    url: str


def mpv_logger(*args) -> None:
    message = args[2]
    log.error(message.rstrip('\n'))


def get_player() -> mpv.MPV:
    p = mpv.MPV(
        log_handler=mpv_logger,
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        ytdl=True,
    )
    p.set_loglevel('error')
    p.fullscreen = False
    p.loop_playlist = 'inf'
    p['vo'] = 'gpu'

    @p.on_key_press('q')
    def my_q_binding():
        p.quit(0)

    return p
