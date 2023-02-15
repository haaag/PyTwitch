# logger.py

import logging

from rich.logging import RichHandler


def set_logging_level(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )


def get_logger(name) -> logging.Logger:
    log = logging.getLogger(name)
    return log
