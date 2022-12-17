# colors.py
# https://github.com/alexandra-zaharia/python-playground
# Thanks to Alexandra Zaharia

from enum import Enum
from enum import auto


class Color(Enum):
    RED = 31
    GREEN = auto()
    YELLOW = auto()
    BLUE = auto()
    MAGENTA = auto()
    CYAN = auto()
    LIGHTRED = 91
    LIGHTGREEN = auto()
    LIGHTYELLOW = auto()
    LIGHTBLUE = auto()
    LIGHTMAGENTA = auto()
    LIGHTCYAN = auto()

    _START = "\u001b["
    _BOLD = ";1"
    _BLINK = ";5"
    _END = "m"
    _RESET = "\u001b[0m"

    @staticmethod
    def error(msg: str) -> str:
        return Color.colored(Color.RED, msg)

    @staticmethod
    def info(msg: str) -> str:
        return Color.colored(Color.YELLOW, msg)

    @staticmethod
    def warning(msg: str) -> str:
        return Color.colored(Color.BLUE, msg)

    @staticmethod
    def red(msg: str) -> str:
        return Color.colored(Color.RED, msg)

    @staticmethod
    def cyan(msg: str) -> str:
        return Color.colored(Color.CYAN, msg)

    @staticmethod
    def green(msg: str) -> str:
        return Color.colored(Color.GREEN, msg)

    @staticmethod
    def colored(color, msg, bold=False, blink=False):
        if not (isinstance(color, Color)):
            raise TypeError(f"Unknown color {color}")

        fmt_msg = Color._START.value + str(color.value)

        if bold:
            fmt_msg += Color._BOLD.value
        if blink:
            fmt_msg += Color._BLINK.value

        return fmt_msg + Color._END.value + str(msg) + Color._RESET.value


if __name__ == "__main__":
    for item in Color:
        if item.name.startswith("_"):
            continue
        print(Color.colored(item, item.name))
        if item.name.startswith("LIGHT"):
            print(Color.colored(item, f"{item.name[5:]} bold == {item.name} bold", bold=True))
