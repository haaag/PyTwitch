# Twitch Menu

## ⭐ About

A user-friendly tool for easily accessing and watching live streams, videos, and clips from Twitch, it presents a menu interface for seamless browsing and streaming.

## 📦 Installation

```bash
# Clone repository
$ git clone "https://github.com/haaag/twitch-menu.git"
$ cd twitch-menu

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate

# Install requirements
$ (.venv) pip install -r requirements.txt
```

## ⚡️ Requirements
* :D
* :D

## 🛠️ Usage

```bash
usage: main.py [-h] [--rofi] [--lines [LINES]] [--player [PLAYER]] [--bottom] [--mixed] [--live] [--test]

Simple tool menu for watching streams live, video or clips from Twitch.

options:
  --rofi             Set launcher to Rofi (default: dmenu)
  --lines [LINES]    Show dmenu in lines (default: 12 lines)
  --player [PLAYER]  Player (default: mpv)
  --bottom           Show dmenu bottom
  --mixed            All channels, live with icon.
  --live             Show live streams
  -h, --help         show this help message and exit
```

## 🖼️ Gifs

![demo](https://github.com/haaag/twitch-menu/raw/main/.github/images/rofi-live.gif)

## 🔗 References and links

- [Twitch API Docs](https://dev.twitch.tv/docs/api/reference)
- [Twitch token generator](https://twitchtokengenerator.com/)
  - Scope: `user:read:follows`
- [Twitch Channel ID and User ID Convertor](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)

## 🧰 TODO

- [ ] Create/Update requirements/dependencies
- [X] Complete Usage
- [X] Update screenshots
- [ ] Finish tests
- https://raw.githubusercontent.com/haaag/{repo_name}/{branch}/.github/images/{asset_name}.{asset_extension}
