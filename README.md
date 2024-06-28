<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>

## Twitch Menu

### ⭐ About

A user-friendly tool for accessing and watching live streams, videos, and
clips from Twitch, it presents a menu interface for seamless browsing and
streaming.

### 📼 Video

https://github.com/haaag/PyTwitch/assets/81921095/e8f07a06-d9dd-47e0-a6d4-f9fba455be16

### ⚡️ Requirements

- Player:
  - 🔹[mpv](https://mpv.io/) _(default)_
- Launcher:
  - [dmenu](https://tools.suckless.org/dmenu/)
  - 🔹[Rofi](https://github.com/davatorium/rofi) _(default)_
  - [fzf](https://github.com/junegunn/fzf) _(WIP)_

### ➕ Dependencies

- [httpx](https://www.python-httpx.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pyselector](https://pypi.org/project/pyselector/)
- [mpv](https://pypi.org/project/mpv/)
- [pydantic](https://pypi.org/project/pydantic/)

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

# Help
(.venv) $ pytwitch --help
```

### ⌨️ Keybinds

| Keybind       | Usage                       |
| ------------- | --------------------------- |
| **alt-k**     | list keybinds               |
| **alt-s**     | search by category or game  |
| **alt-v**     | list channel's videos       |
| **alt-t**     | filter by category or game  |
| **alt-c**     | search by channel           |
| **alt-o**     | open stream chat in browser |
| **alt-i**     | show item information       |
| **alt-m**     | show top streams            |
| **alt-q**     | quit                        |
| ~~**alt-m**~~ | ~~multi-select streams~~    |

### 🔗 References

- [Twitch API](https://dev.twitch.tv/docs/api/)
- [Twitch API Reference](https://dev.twitch.tv/docs/api/reference)

### 🧰 TODO

- [ ] Finish tests
- [x] Create/Update requirements/dependencies
- [x] Complete Usage
- [x] Update screenshots
- [x] Better logging
- [x] Update GIFs
- [x] Update `argparse` help
- [x] Display `keybinds`

- [ignore](https://raw.githubusercontent.com/haaag/{repo_name}/{branch}/.github/images/{asset_name}.{asset_extension})
