# app.py

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

from httpx import URL
from pyselector import Menu

from .player import create_player
from .utils import logger

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

    from .datatypes import BroadcasterInfo
    from .twitch import TwitchClient


log = logger.get_logger(__name__)


def load_stream(player_name: str, endpoint: str) -> int:
    if endpoint.startswith("http"):
        player = create_player("mpv")
        return player.play(endpoint)

    player = create_player(player_name)
    url = URL("https://www.twitch.tv/").join(endpoint)
    return player.play(url)


def handle_selection_old(
    client: TwitchClient,
    prompt: Callable[..., Any],
    menu: MenuInterface,
    **kwargs: Any,
) -> str:
    code = kwargs.pop("keycode")
    if code == 0:
        return extract_username_from_str(kwargs.pop("item"))
    keybinds: dict[int, Callable[..., Any]] = {
        keybind.code: keybind.callback for keybind in menu.keybind.list_registered
    }
    if code in keybinds:
        keybinds[code](client, prompt, menu, keybind=keybinds[code], **kwargs)
    return "<<<ERRORRRRRRR>>>"


def handle_selection(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    code = kwargs.pop("keycode")
    if code == 0:
        return extract_username_from_str(kwargs.pop("item"))
    for keybind in menu.keybind.list_registered:
        if keybind.code == code:
            keybind.toggle_hidden()
            return keybind.callback(client, prompt, menu, keybind=keybind, **kwargs)
    return ""


def get_launcher(name: str):
    launchers = {
        "rofi": Menu.rofi(),
        "dmenu": Menu.dmenu(),
        "fzf": Menu.fzf(),
    }
    return launchers[name]


def extract_username_from_str(stream_str: str) -> str:
    log.info("processing: %s", stream_str)
    live_icon = "●"
    if live_icon not in stream_str:
        return stream_str
    username_start = stream_str.find("● ") + 2
    username_end = stream_str.find(" ", username_start)
    log.info("extracted: %s", stream_str[username_start:username_end])
    return stream_str[username_start:username_end]


def display_live_follows(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    live = [str(channel) for channel in client.channels.followed_streams_live]
    item, keycode = prompt(
        items=live,
        mesg=f"> {len(live)} live channels.",
        prompt="twitch live>",
    )
    return handle_selection(client, prompt, menu, item=item, keycode=keycode)


def display_all_follows(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    follows = [str(follow) for follow in client.channels.follows]
    item, keycode = prompt(items=follows)
    return handle_selection(client, prompt, menu, item=item, keycode=keycode)


def display_follow_clips(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    follow = kwargs.pop("follow")
    clips = client.clips.get_clips(follow.broadcaster_id)

    if not clips:
        raise ValueError("No clips...display_follow_videos")

    items = {f"({i}) {str(clip)}": clip.url for i, clip in enumerate(clips)}
    mesg = f"> Showing {len(items)} clips from channel <{follow.broadcaster_name}>"
    item, code = prompt(items=list(items.keys()), mesg=mesg)

    if item not in list(items.keys()):
        raise ValueError(f"{item=} not found")
    return items[item]


def display_follow_videos(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    follow = kwargs.pop("follow")
    videos = client.channels.get_videos(follow.broadcaster_id)

    if not videos:
        raise ValueError("No videos...display_follow_videos")

    items = {f"({i}) {str(video)}": video.url for i, video in enumerate(videos)}
    item, code = prompt(items=list(items.keys()))

    if item not in list(items.keys()):
        raise ValueError(f"{item=} not found")

    return items[item]


def display_follow_info(
    client: TwitchClient,
    prompt: Callable,
    menu: MenuInterface,
    **kwargs,
) -> str:
    username = extract_username_from_str(kwargs.pop("item"))
    follow = client.channels.get_info_from_username(username)
    menu.keybind.toggle_all()

    if follow is None:
        log.error("Not found: %s", username)
        return handle_selection(client, prompt, menu, **kwargs)

    clips_keybind = menu.keybind.add(
        key="alt-p",
        description="show clips",
        callback=display_follow_clips,
    )

    videos_keybind = menu.keybind.add(
        key="alt-v",
        description="show videos",
        callback=display_follow_videos,
    )

    data = build_data_info(client, follow)
    item, keycode = prompt(items=data)
    menu.keybind.toggle_all()
    clips_keybind.toggle_hidden()
    videos_keybind.toggle_hidden()
    return handle_selection(client, prompt, menu, item=item, keycode=keycode, follow=follow)


def build_data_info(client: TwitchClient, follow: BroadcasterInfo) -> list[str]:
    data = []
    data.append(f"Category: {follow.game_name}")
    if client.channels.is_online(follow.broadcaster_id):
        data.append(f"{client.live_icon} Live Stream: {follow.title}")
    else:
        data.append(f"Last Stream: {follow.title}")
    data.append("-" * len(data[1]))
    # data.append("Videos: Get videos")
    # data.append("Clips: Get clips")
    return data
