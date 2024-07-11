<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>

## Twitch Menu

### ⭐ About

A user-friendly tool for accessing and watching live streams, videos, and clips
from Twitch.

### 📼 Video

https://github.com/haaag/PyTwitch/assets/81921095/e8f07a06-d9dd-47e0-a6d4-f9fba455be16

### ⚡️ Requirements

- Player:
  - [mpv](https://mpv.io/)
- Launcher:
  - 🔹[Rofi](https://github.com/davatorium/rofi) <sub>_(default)_</sub>
  - [dmenu](https://tools.suckless.org/dmenu/)
  - [fzf](https://github.com/junegunn/fzf)

### 🔒Credentials

For authentication, you can set environment vars in your `shell` and export them or use the
`.env` file and put it in the root of the project.

[env-template](https://github.com/haaag/pytwitch/blob/main/env-template) file

```bash
# Twitch credentials
TWITCH_CLIENT_ID="xxxxx"
TWITCH_ACCESS_TOKEN="xxx"
TWITCH_USER_ID="123456"
```

#### 🔓Credentials directions

- [Twitch token generator](https://twitchtokengenerator.com/)
  - Scope: `user:read:follows`
- [Twitch Channel ID and User ID Converter](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)

### 📦 Installation

```bash
# Clone repository
$ git clone "https://github.com/haaag/pytwitch.git"
$ cd pytwitch

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate

# Install requirements
(.venv) $ pip install -r requirements.txt

# Install
(.venv) $ pip install .
```

### 🛠️ Usage

After installation you can use the command `pytwitch`

Or use a **alias** like `alias pt='pytwitch -e ~/path/to/envfile/.env'`

```bash
$ pytwtich -h
Simple tool menu for watching streams, videos from twitch.

arguments:
    -m, --menu          select menu [rofi|dmenu] (default: rofi)
    -e, --env           path to env file
    -C, --channel       search by channel query
    -G, --games         search by game or category
    -v, --verbose       increase verbosity (use -v, -vv, or -vvv)
    -h, --help          show this help

options:
    --no-markup         disable pango markup (rofi)
    --no-conf           disable `mpv` configuration
```

### ⌨️ Keybinds <sub>_Rofi only_</sub>

| Keybind       | Usage                       |
| ------------- | --------------------------- |
| **alt-k**     | list keybinds               |
| **alt-s**     | search by category or game  |
| **alt-c**     | search by channel           |
| **alt-v**     | list channel's videos       |
| **alt-t**     | group by category or game   |
| **alt-o**     | open stream chat in browser |
| **alt-i**     | show item information       |
| **alt-m**     | show top streams            |
| **alt-g**     | show top games with streams |
| ~~**alt-m**~~ | ~~multi-select streams~~    |

### 🔗 References

- [Twitch API](https://dev.twitch.tv/docs/api/)
- [Twitch API Reference](https://dev.twitch.tv/docs/api/reference)

### ➕ Dependencies

- [httpx](https://www.python-httpx.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pyselector](https://pypi.org/project/pyselector/)
- [mpv](https://pypi.org/project/mpv/)
- [pydantic](https://pypi.org/project/pydantic/)
- [tenacity](https://pypi.org/project/tenacity/)

### 🧰 TODO

- [ ] Finish tests
- [x] Create/Update requirements/dependencies
- [x] Complete Usage
- [x] Update screenshots
- [x] Better logging
- [x] Update GIFs
- [x] Update `argparse` help
- [x] Display `keybinds`
