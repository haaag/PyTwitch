# logger.py

from __future__ import annotations

import logging

from rich.logging import RichHandler


def set_logging_level(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s - %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )


def get_logger(name) -> logging.Logger:
    return logging.getLogger(name)