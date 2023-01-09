# app.py

import functools
import sys
from typing import Callable
from typing import Iterable
from typing import Optional

from httpx import URL

from twitch.datatypes import BroadcasterInfo
from twitch.datatypes import ChannelUserFollows
from twitch.datatypes import MenuOptions
from twitch.datatypes import TwitchClip
from twitch.datatypes import TwitchClips
from twitch.twitch import TwitchClient
from twitch.utils.colors import Color as C
from twitch.utils.executor import Executor
from twitch.utils.logger import get_logger
from twitch.utils.menu import Menu

log = get_logger(__name__)


class App:
    """
    This class is responsible for handling the main application flow,
    including the interaction with the user through a command line interface,
    and performing requests to the Twitch API through the `TwitchClient` object.

    """

    def __init__(self, twitch: TwitchClient, menu: Menu, player: str) -> None:
        """
        Initializes the app with the specified client, menu, and execution options.
        """
        self.twitch = twitch
        self.menu = menu
        self._executor = Executor(player)
        self._user_follows: Optional[Iterable[ChannelUserFollows]] = None
        self.tv = URL("https://www.twitch.tv/")

    @property
    def user_follows(self) -> Iterable[ChannelUserFollows]:
        if not self._user_follows:
            self._user_follows = self.twitch.channels.follows
            return self._user_follows
        return self._user_follows

    def load_stream_selected(self, stream: str) -> None:
        url = self.tv.join(stream)
        log.info("%s stream %s with %s", C.info("Opening"), C.red(stream), C.green(self._executor.bin))  # type: ignore
        self._executor.notification(f"Opening stream <b>{stream}</b>")
        self._executor.launch(url)

    def load_clip_selected(self, clip: TwitchClip) -> None:
        """Load a selected clip by its URL."""
        log.info(
            "%s stream %s with %s",
            C.info("Opening"),
            C.red(clip.title),
            C.green(self._executor.bin),  # type: ignore
        )
        self._executor.notification(f"Opening clip <b>{clip.broadcaster_name}@{clip.title}</b>")
        self._executor.launch(clip.url)

    def clean_channel_name(self, name: str) -> str:
        # FIX: Extract method from class
        if self.twitch.live_icon in name:
            return name.replace(self.twitch.live_icon, "").replace("(live)", "").strip()
        return name.strip()

    def show_items(
        self, options: list[str], fallback_fn: Optional[Callable] = None, prompt: str = "twitch:", back: bool = False
    ) -> Optional[str]:
        selected = self.menu.show_items(self._executor, options, prompt=prompt, back=back)

        if not selected:
            return None

        if selected not in options:
            self.handle_missing_option(selected)
            if fallback_fn:
                fallback_fn()
            sys.exit(1)

        if selected == self.menu.back and fallback_fn is not None:
            fallback_fn()

        return selected

    def handle_missing_option(self, selected: str) -> None:
        log.warning("Option %s not found.", C.red(selected))
        self.show_items([f"Option '{selected}' selected not found."])

    def show_no_results_message(self, log_msg: str) -> None:
        log.warning(log_msg)
        self.menu.show_items(self._executor, [log_msg])

    def show_online_follows(self) -> None:
        """
        Show the channels that the user follows that are currently live.
        """
        streams_online = self.twitch.channels.followed_streams_live

        if not streams_online:
            self.show_no_results_message("No online followed channels")
            return None

        items = {channel.user_name: channel for channel in self.twitch.channels_live_for_menu}
        options = list(items.keys())
        selected = self.show_items(options=options, prompt="live:", back=True)

        if selected is None:
            sys.exit(0)

        selected = self.clean_channel_name(selected).split("|")[0]
        self.load_stream_selected(selected.strip())
        return None

    def show_follows_and_online(self) -> None:
        """
        Shows a list of channels that the user follows and highlights those who are live.
        """
        follow = self.show_follows(highlight_live=True)
        if not follow:
            return None
        return self.show_info(follow.to_id)

    def show_follows(self, highlight_live: bool) -> Optional[ChannelUserFollows]:
        """Shows a list of channels that the user follows."""
        follows = {user.to_name: user for user in self.user_follows}
        follows_names = list(follows.keys())

        if highlight_live:
            for channel in self.twitch.channels.followed_streams_live:
                if channel.user_name in follows_names:
                    idx = follows_names.index(channel.user_name)
                    follows_names[idx] = f"{self.twitch.live_icon} {channel.user_name} (live)"

        selected = self.show_items(follows_names, fallback_fn=self.show_menu, prompt="'twitch follows:'", back=True)

        if selected is None:
            sys.exit(1)

        selected = self.clean_channel_name(selected)
        return follows[selected]

    def show_videos(self, channel: BroadcasterInfo) -> None:
        """Shows a list of videos for the specified channel."""
        channel_videos = self.twitch.channels.get_videos(user_id=channel.broadcaster_id)

        videos_dict = {
            f"{idx} {self.menu.unicode.BULLET_ICON} {video.title} | {video.duration} (views: {video.view_count})": video
            for idx, video in enumerate(channel_videos)
        }

        if not videos_dict:
            self.show_no_results_message(f"No available videos from followed channel: {channel.broadcaster_name}")
            return self.show_info(channel.broadcaster_id)

        fallback = functools.partial(self.show_info, channel.broadcaster_id)
        selected = self.show_items(
            list(videos_dict.keys()),
            fallback_fn=fallback,
            prompt=f"'{channel.broadcaster_name} videos:'",
            back=True,
        )

        if selected is None:
            sys.exit(0)

        video = videos_dict[selected]
        self.load_stream_selected(video.url)
        return self.show_videos(channel)

    def show_menu(self) -> None:
        """
        Displays the main menu of the app, with options to view online channels
        and channels that the user follows.
        """
        menu_options: MenuOptions = {
            f"{self.menu.unicode.BULLET_ICON} All follows": self.show_follows_and_online,
            f"{self.menu.unicode.BULLET_ICON} Live followed": self.show_online_follows,
        }

        options_keys = list(menu_options.keys())
        selected = self.show_items(options=options_keys)

        if not selected:
            sys.exit(1)

        menu_options[selected]()

        sys.exit(0)

    def show_info(self, user_id: str) -> None:
        """
        Shows information about a specific channel, including the channel's name, status, game being played,
        and a menu to view the channel's videos or schedule.

        Args:
        user_id (str): The ID of the channel to display information for.

        Returns:
        None: The selected option is executed.
        """
        channel = self.twitch.channels.information(user_id)

        menu_info = []
        category = f"Category: {channel.game_name}"
        menu_info.append(f"Name: {channel.broadcaster_name}")
        menu_info.append(category)
        if self.twitch.channels.is_online(user_id):
            menu_info.append(f"{self.twitch.live_icon} Live Stream: {channel.title}")
        else:
            menu_info.append(f"Last Stream: {channel.title}")
        menu_info.append("-" * len(category))
        menu_info.append("Videos: Get videos (This can take a couple of seconds)")
        menu_info.append("Clips: Get clips (This can take a couple of seconds)")

        selected = self.show_items(
            menu_info,
            fallback_fn=self.show_follows_and_online,
            prompt=f"'{channel.broadcaster_name} info:'",
            back=True,
        )

        if not selected:
            sys.exit(1)

        if selected.startswith("Clips"):
            self.show_clips(channel)

        if selected.startswith("Videos"):
            self.show_videos(channel)

        if selected.startswith("Last"):
            print("Selected:", selected)
            raise NotImplementedError()

        if selected.startswith(self.twitch.live_icon):
            self.load_stream_selected(channel.broadcaster_name)

        self.show_info(user_id)

    def show_clips(
        self,
        channel: BroadcasterInfo,
        clips: Optional[TwitchClips] = None,
    ) -> None:
        """
        Shows the list of clips for the specified user and allows the user to select a clip to play.

        Args:
        channel (BroadcasterInfo): The channel object to display clips for.

        Returns:
        None: The selected clip is played.
        """
        if not clips:
            clips = self.twitch.clips.get_clips(channel.broadcaster_id)

        clips_dict = {
            f"{idx} {self.menu.unicode.BULLET_ICON} {c.title} | creator: {c.creator_name} ({c.view_count} views)": c
            for idx, c in enumerate(clips)
        }

        if not clips_dict:
            self.show_no_results_message(f"No available clips from followed channel: {channel.broadcaster_name}")
            self.show_info(channel.broadcaster_id)

        selected = self.show_items(
            options=list(clips_dict.keys()),
            fallback_fn=functools.partial(self.show_info, channel.broadcaster_id),
            prompt=f"'{channel.broadcaster_name} clips:'",
            back=True,
        )
        if not selected:
            sys.exit(1)

        clip = clips_dict[selected]
        self.load_clip_selected(clip)
        self.show_clips(channel, list(clips_dict.values()))
