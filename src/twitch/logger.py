# logger.py

from __future__ import annotations

import logging


class C:
    DEBUG = '\33[37;2m'
    BOLD_RED = '\033[31;1;6m'
    RED = '\33[31m'
    YELLOW = '\33[33m'
    CYAN = '\33[36m'
    RESET = '\33[0m'


FMT = '[{levelname:^7}] {name:<30}: {message} (line:{lineno})'

FORMATS = {
    logging.DEBUG: f'{C.DEBUG}{FMT}{C.RESET}',
    logging.INFO: f'{C.CYAN}{FMT}{C.RESET}',
    logging.WARNING: f'{C.YELLOW}{FMT}{C.RESET}',
    logging.ERROR: f'{C.RED}{FMT}{C.RESET}',
    logging.CRITICAL: f'{C.BOLD_RED}{FMT}{C.RESET}',
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style='{')
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())


def verbose(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.ERROR,
        handlers=[handler],
    )
