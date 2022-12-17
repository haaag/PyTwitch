# logger.py

import logging

from twitch.utils.colors import Color as C


def set_logging_level(level: int) -> None:
    levels = {
        20: C.info("[%(levelname)s]"),
        30: C.warning("[%(levelname)s]"),
        40: C.error("[%(levelname)s]"),
    }
    levelname = levels.get(level)
    logging.basicConfig(level=level, format=f"{levelname}:%(name)s - %(message)s")


def get_logger(name) -> logging.Logger:
    log = logging.getLogger(name)
    return log
