# executor.py

from __future__ import annotations

import subprocess
import typing

from .helpers import secure_split
from .logger import get_logger

if typing.TYPE_CHECKING:
    from httpx import URL

log = get_logger(__name__)


def run(commands: str, items: list[str]) -> str:
    commands_split = secure_split(commands)
    log_msg = f"Running [red bold]{commands_split[0]}[/] with args: [yellow]{commands_split}[/]"
    log.debug("%s", log_msg)

    with subprocess.Popen(
        commands_split,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ) as proc:
        bytes_items = "\n".join(items).encode()
        selected, _ = proc.communicate(input=bytes_items)
    return selected.decode(encoding="utf-8").strip()


def launch(url: str | URL) -> int:
    log_msg = f"[red bold]Launching 'mpv' with args:[/] {url}"
    log.debug("%s", log_msg)
    command_with_args = secure_split(f"mpv {url}")
    subprocess.call(command_with_args, stderr=subprocess.DEVNULL)
    return 0


def notification(message: str) -> subprocess.Popen[bytes]:
    notification_str = f"notify-send -i twitch-indicator 'Twitch' '{message}'"
    command = secure_split(notification_str)
    return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
