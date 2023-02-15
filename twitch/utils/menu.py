# menu.py
# -*- coding: utf-8 -*-

import sys
from typing import Optional
from typing import Protocol
from typing import Text
from typing import Union

from twitch.utils.executor import Executor


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


class Menu(Protocol):
    command: str
    unicode: MenuUnicodes
    back: Text
    exit: Text
    lines: Optional[int]

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        raise NotImplementedError()


class Dmenu:
    def __init__(self, lines: Optional[int] = None) -> None:
        self.command = "dmenu"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK} Back"
        self.exit = f"{self.unicode.EXIT} Exit"
        self.lines = lines

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        case_insensitively = "-i"
        command_str = f"{case_insensitively}"

        if extra.get("back"):
            items.append(self.back)

        if extra.get("exit"):
            items.append(self.unicode.EXIT)

        if self.lines:
            command_str += f" -l {self.lines}"

        command_str += f" -p {prompt}"

        item = executor.run(self.command, command_str, items)

        if item == "" or item is None:
            return None

        return item


class Rofi:
    def __init__(self, lines: Optional[int] = None) -> None:
        self.command = "rofi"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK} Back"
        self.exit = f"{self.unicode.EXIT} Exit"
        self.lines = lines

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        command_str = f"-dmenu -i -p {prompt}"

        if extra.get("back"):
            items.append(self.back)

        items.append(self.exit)

        if extra.get("lines"):
            lines = extra.get("lines")
            command_str += f" -l {lines}"

        command_str += " -theme-str 'window {width: 45%; height: 35%; text-align: center;}'"
        item = executor.run(self.command, command_str, items)

        if item == self.exit:
            sys.exit(0)

        if item == "" or item is None:
            return None

        return item


def get_menu(*, rofi: bool = False, lines: Optional[int] = None) -> Union[Dmenu, Rofi]:
    return Rofi(lines) if rofi else Dmenu(lines)
