# executor.py

import shlex
import shutil
import subprocess
from typing import Optional

from httpx import URL

from twitch.utils.logger import get_logger

log = get_logger(__name__)


class ExecutableNotFound(Exception):
    def __init__(self, message):
        self.message = f"Executable '{message}' not found."
        super().__init__(self.message)


class Executor:
    def __init__(self, player: str) -> None:
        self.player = player
        self.bin = shutil.which(player)

        if not self.bin:
            raise ExecutableNotFound(self.player)

    def run(self, executable: str, commands: str, items: list[str]) -> Optional[str]:
        if not shutil.which(executable):
            raise ExecutableNotFound(executable)

        args_splitted = shlex.split(f"{executable} {commands}")

        with subprocess.Popen(
            args_splitted, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as proc:

            bytes_items = "\n".join(items).encode()
            selected, _ = proc.communicate(input=bytes_items)

        if selected:
            return selected.decode(encoding="utf-8")
        return None

    def launch(self, url: str | URL) -> int:
        if not self.bin:
            raise ExecutableNotFound(self.player)

        args = shlex.split(f"{self.player} {url}")
        subprocess.call(args, stderr=subprocess.DEVNULL)
        return 0

    def notification(self, message: str) -> subprocess.Popen[bytes]:
        notification_str = f"notify-send -i twitch-indicator 'Dmenu-Twitch' '{message}'"
        command: list[str] = shlex.split(notification_str)
        return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
