# utils.py

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
import time
from functools import wraps
from typing import Callable
from typing import NamedTuple

log = logging.getLogger(__name__)


class Clipboard(NamedTuple):
    copy: str
    paste: str


def get_clipboard() -> Clipboard:
    # TODO: [ ] add support for other platforms
    clipboards: dict[str, Clipboard] = {
        'xclip': Clipboard(
            copy='xclip -selection clipboard',
            paste='xclip -selection clipboard -o',
        ),
        'xsel': Clipboard(
            copy='xsel -b -i',
            paste='xsel -b -o',
        ),
    }
    for name, clipboard in clipboards.items():
        if shutil.which(name):
            log.info(f'clipboard command: {clipboard!r}')
            return clipboard
    err_msg = 'No suitable clipboard command found.'
    log.error(err_msg)
    raise FileNotFoundError(err_msg)


def copy_to_clipboard(item: str) -> int:
    """Copy selected item to the system clipboard."""
    data = item.encode('utf-8', errors='ignore')
    args = shlex.split(get_clipboard().copy)
    try:
        with subprocess.Popen(args, stdin=subprocess.PIPE) as proc:  # noqa: S603
            proc.stdin.write(data)  # type: ignore[union-attr]
            log.debug("Copied '%s' to clipboard", item)
    except subprocess.SubprocessError as e:
        log.error("Failed to copy '%s' to clipboard: %s", item, e)
        return 1
    return 0


def timeit(func: Callable) -> Callable:
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        log.info(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def secure_split(command: str) -> list[str]:
    try:
        command_split: list[str] = shlex.split(command)
    except ValueError:
        command = command.replace("'", '')
        command_split = shlex.split(command)
    return command_split
