# menu.py

from __future__ import annotations

import sys
from typing import Optional
from typing import Protocol
from typing import Text
from typing import Union

from . import executor


class MenuUnicodes:
    BACK: Text = "\u21B6"
    BULLET_ICON: Text = "\u2022"
    CALENDAR: Text = "\U0001F4C5"
    CIRCLE: Text = "\u25CF"
    CLOCK: Text = "\U0001F559"
    CROSS: Text = "\u2716"
    DELIMITER: Text = "\u2014"
    EXIT: Text = "\uf842"
    EYE: Text = "\U0001F441"
    HEART: Text = "\u2665"
    BELL: Text = "\uf0f3"
    UNBELL: Text = "\uf1f6"


class Menu(Protocol):
    command: str
    unicode: MenuUnicodes
    back: Text
    exit: Text
    lines: Optional[int]

    @property
    def args(self) -> list[str]:
        raise NotImplementedError

    def show_items(self, items: list[str], prompt: str = "twitch:", **extra) -> str:
        raise NotImplementedError


class Dmenu:
    def __init__(self, lines: Optional[int] = None) -> None:
        self.command = "dmenu"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK} Back"
        self.exit = f"{self.unicode.EXIT} Exit"
        self.lines = lines

    @property
    def args(self) -> list[str]:
        return [
            self.command,
            "-i",  # Set filter to be case insensitive
        ]

    def show_items(self, items: list[str], prompt: str = "twitch:", **extra) -> str:
        commands = self.args
        commands.append(f"-p {prompt}")

        items.append(self.exit)

        if extra.get("back"):
            items.append(self.back)

        if self.lines:
            commands.append(f"-l {self.lines}")

        item = executor.run(" ".join(commands), items)

        if item == self.exit or item == "" or item is None:
            sys.exit(1)

        return item


class Rofi:
    def __init__(self, lines: Optional[int] = None) -> None:
        self.command = "rofi"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK} Back"
        self.exit = f"{self.unicode.EXIT} Exit"
        self.lines = lines

    @property
    def args(self) -> list[str]:
        return [
            self.command,
            "-dmenu",
            "-i",  # Set filter to be case insensitive
            "-theme-str 'window {width: 50%; height: 40%; text-align: center;}'",
        ]

    def show_items(self, items: list[str], prompt: str = "twitch:", **extra) -> str:
        commands = self.args
        commands.append(f"-p {prompt}")

        items.append(self.exit)

        if extra.get("back"):
            items.append(self.back)

        if extra.get("mesg"):
            msg = extra.get("mesg")
            commands.append(f" -mesg '{msg}'")

        if self.lines:
            commands.append(f"-l {self.lines}")

        item = executor.run(" ".join(commands), items)

        if item == self.exit or item == "" or item is None:
            sys.exit(1)

        return item


def get_menu(*, rofi: bool = False, lines: Optional[int] = None) -> Union[Dmenu, Rofi]:
    return Rofi(lines) if rofi else Dmenu(lines)
