# menu.py

from typing import Optional
from typing import Protocol
from typing import Text
from typing import Union

from twitch.utils.executor import Executor


class MenuUnicodes:
    HEART: Text = "\u2665"  # ♥ Heart
    CIRCLE: Text = "\u25CF"  # ● Circle
    BULLET_ICON: Text = "\u2022"  # • Small circle
    BACK_ARROW: Text = "\u2190"  # ← Left arrow


class Menu(Protocol):
    name: str
    unicode: MenuUnicodes
    back: Text
    lines: Optional[int]
    bottom: bool

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        raise NotImplementedError()


class TestDmenu:
    def __init__(self, lines: Optional[int] = None, bottom: bool = False) -> None:
        self.name = "dmenu"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK_ARROW} Back"
        self.lines = lines
        self.bottom = bottom

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        case_insensitively = "-i"
        command_str = f"{case_insensitively}"

        if extra.get("back"):
            items.append(self.back)

        if self.lines:
            command_str += f" -l {self.lines}"

        if self.bottom:
            command_str += " -b"

        command_str += f" -p {prompt}"

        item = executor.run(self.name, command_str, items)

        if item == "" or item is None:
            return None

        return item.strip()


class Dmenu:
    def __init__(self) -> None:
        self.name = "dmenu"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK_ARROW} Back"

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        case_insensitively = "-i"
        command_str = f"{case_insensitively}"

        if extra.get("back"):
            items.append(self.back)

        if extra.get("delete"):
            items.append("Delete")

        if extra.get("lines"):
            lines = extra.get("lines")
            command_str += f" -l {lines}"

        if extra.get("bottom"):
            command_str += " -b"

        command_str += f" -p {prompt}"

        item = executor.run(self.name, command_str, items)

        if item == "" or item is None:
            return None

        return item.strip()


class Rofi:
    def __init__(self, lines: Optional[int] = None, bottom: bool = False) -> None:
        self.name = "rofi"
        self.unicode = MenuUnicodes()
        self.back = f"{self.unicode.BACK_ARROW} Back"
        self.lines = lines
        self.bottom = bottom

    def show_items(self, executor: Executor, items: list[str], prompt: str = "twitch:", **extra) -> Optional[str]:
        command_str = f"-dmenu -i -p {prompt}"

        if extra.get("back"):
            items.append(self.back)

        if extra.get("delete"):
            items.append("Delete")

        if extra.get("lines"):
            lines = extra.get("lines")
            command_str += f" -l {lines}"

        command_str += " -theme-str 'window {width: 65%; height: 40%; text-align: center;}'"
        item = executor.run(self.name, command_str, items)

        if item == "" or item is None:
            return None

        return item.strip()


def get_menu(*, rofi: bool = False, lines: Optional[int] = None, bottom: bool = False) -> Union[TestDmenu, Rofi]:
    return Rofi(lines, bottom) if rofi else TestDmenu(lines, bottom)
