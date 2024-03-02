from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
from typing import NamedTuple

logger = logging.getLogger(__name__)


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
            logger.info(f'clipboard command: {clipboard!r}')
            return clipboard
    err_msg = 'No suitable clipboard command found.'
    logger.error(err_msg)
    raise FileNotFoundError(err_msg)


def copy(item: str) -> int:
    """Copy selected item to the system clipboard."""
    data = item.encode('utf-8', errors='ignore')
    args = shlex.split(get_clipboard().copy)
    try:
        with subprocess.Popen(args, stdin=subprocess.PIPE) as proc:  # noqa: S603
            proc.stdin.write(data)  # type: ignore[union-attr]
            logger.debug("Copied '%s' to clipboard", item)
    except subprocess.SubprocessError as e:
        logger.error("Failed to copy '%s' to clipboard: %s", item, e)
        return 1
    return 0
