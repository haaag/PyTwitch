<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=Flat&logo=sqlite&logoColor=white) 
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) 
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>


# Twitch Menu

## ⭐ About

A user-friendly tool for easily accessing and watching live streams, videos, and clips from Twitch, it presents a menu interface for seamless browsing and streaming.
`Using 'streamlink' as default player, since using only 'mpv' the ads are very aggressive.`

## ⚡️ Requirements

* Player:
  * [streamlink](https://streamlink.github.io/) _(recommended)_
  * ⭐ [mpv](https://mpv.io/)
* Launcher:
  * [dmenu](https://tools.suckless.org/dmenu/)
  * [Rofi](https://github.com/davatorium/rofi)

## ➕ Dependencies

* [httpx](https://www.python-httpx.org/)
* [rich](https://github.com/Textualize/rich)

## 🔒Credentials

In this project, the library [python-dotenv](https://pypi.org/project/python-dotenv/) is used to read the credentials in the `.env` file (reference [env-template](https://github.com/haaag/twitch-menu/blob/main/env-template) file)

```bash
# Twitch credentials
# Rename file 'env-template' to .env
TWITCH_CLIENT_ID=xxxxx
TWITCH_ACCESS_TOKEN=xxx
TWITCH_USER_ID=00000
```

### 🔓Credentials directions

* [Twitch token generator](https://twitchtokengenerator.com/)
  * Scope: `user:read:follows`
* [Twitch Channel ID and User ID Convertor](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)

## 📦 Installation

```bash
# Clone repository
$ git clone "https://github.com/haaag/twitch-menu.git"
$ cd twitch-menu

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate

# Install requirements
(.venv) $ pip install -r requirements.txt
```

## 🛠️ Usage

```bash
# Run main.py with default launcher 'dmenu'
(.venv) $ python main.py

# Run main.py with launcher 'rofi'
(.venv) $ python main.py --rofi

# help
(.venv) $ python main.py --help

# Output
usage: main.py [-h] [--rofi] [--lines [LINES]] [--player [PLAYER]] [--live]

Simple tool menu for watching streams live, video or clips from Twitch.

options:
  --rofi             Set launcher to Rofi (default: dmenu)
  --lines            Show dmenu in lines (default: 12 lines)
  --player           Player (default: mpv)
  --live             Show live streams only
  -v, --verbose      Verbose mode
  -h, --help         show this help message and exit
```

## 🖼️ Gifs

![demo](https://github.com/haaag/twitch-menu/raw/main/.github/images/rofi-live.gif)

## 🔗 References

* [Twitch API](https://dev.twitch.tv/docs/api/)
* [Twitch API Reference](https://dev.twitch.tv/docs/api/reference)

## 🧰 TODO

* [ ] Create/Update requirements/dependencies
* [X] Complete Usage
* [X] Update screenshots
* [X] Better logging
* [ ] Finish tests
* [ignore](https://raw.githubusercontent.com/haaag/{repo_name}/{branch}/.github/images/{asset_name}.{asset_extension})
