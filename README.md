<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>

## Twitch Menu

### ⭐ About

A user-friendly tool for easily accessing and watching live streams, videos, and
clips from Twitch, it presents a menu interface for seamless browsing and
streaming.

### ⚡️ Requirements

- Player:
  - ▪️[mpv](https://mpv.io/)
- Launcher:
  - [dmenu](https://tools.suckless.org/dmenu/)
  - ▪️[Rofi](https://github.com/davatorium/rofi)
  - [fzf](https://github.com/junegunn/fzf) _(WIP)_

### ➕ Dependencies

- [httpx](https://www.python-httpx.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pyselector](https://pypi.org/project/pyselector/)
- [xlib](https://pypi.org/project/xlib/)
- [mpv](https://pypi.org/project/mpv/)

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

```bash
# Use rofi menu by default
(.venv) $ pytwitch

# You can use it with dmenu or rofi
(.venv) $ pytwitch -m dmenu

# Using path to env file
(.venv) $ pytwitch -c ./.env

# Add args to player (default mpv)
(.venv) $ pytwitch --player --player-args='--no-resume-playback'

# Help
(.venv) $ pytwitch --help
```

### 🖼️ ~~Gifs~~

![demo](https://github.com/haaag/twitch-menu/raw/main/.github/images/rofi-live.gif)

### 🔗 References

- [Twitch API](https://dev.twitch.tv/docs/api/)
- [Twitch API Reference](https://dev.twitch.tv/docs/api/reference)

### 🧰 TODO

- [x] Create/Update requirements/dependencies
- [x] Complete Usage
- [x] Update screenshots
- [x] Better logging
- [ ] Finish tests
- [ ] Update GIFs
- [ ] Update `argparse` help

  - [ ] Display `keybinds`

- [ignore](https://raw.githubusercontent.com/haaag/{repo_name}/{branch}/.github/images/{asset_name}.{asset_extension})
