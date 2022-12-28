# app.py

import functools
import sys
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
        if self.twitch.live_icon in name:
            strip_str = name.replace(self.twitch.live_icon, "")
            return strip_str.strip()
        return name.strip()

    def show_online_follows(self) -> Optional[str]:
        """
        Show the channels that the user follows that are currently live.

        Returns:
        str: The name of the selected channel if a channel was selected, None otherwise.
        """
        streams_online = self.twitch.channels_live

        if not streams_online:
            log.warning("No %s followed channels", C.red("online"))
            self.menu.show_items(self._executor, ["No online followed channels"])
            return None

        items = {channel.user_name: channel for channel in self.twitch.channels_live_for_menu}
        options = list(items.keys())
        selected = self.menu.show_items(self._executor, options, prompt="live:", back=True)

        if not selected:
            return None

        if selected not in options:
            log.warning("Live stream %s not found.", C.red(selected))
            self.menu.show_items(
                self._executor, [f"Live stream '{selected}' not found."], prompt="'twitch follows:'", back=True
            )
            self.show_online_follows()

        if selected == self.menu.back:
            self.show_menu()

        if self.twitch.live_icon in selected:
            selected = selected.replace(self.twitch.live_icon, "").split("|")[0]
            self.load_stream_selected(selected.strip())
            self.show_online_follows()

        return selected

    def show_follows_and_online(self) -> None:
        """
        Shows a list of channels that the user follows.
        (Live channels have a '●')
        """
        follows = {user.to_name: user for user in self.user_follows}
        follows_names = list(follows.keys())

        for channel in self.twitch.channels_live:
            if channel.user_name in follows_names:
                idx = follows_names.index(channel.user_name)
                follows_names[idx] = f"{self.twitch.live_icon} {channel.user_name}"

        selected = self.menu.show_items(self._executor, follows_names, prompt="'twitch follows:'", back=True)

        if not selected:
            sys.exit(1)

        if selected == self.menu.back:
            self.show_menu()

        if selected not in follows_names:
            log.warning("Channel %s not found.", C.red(selected))
            self.menu.show_items(
                self._executor, [f"Channel '{selected}' not found."], prompt="'twitch follows:'", back=True
            )
            self.show_follows_and_online()

        selected = self.clean_channel_name(selected)

        follow = follows[selected]

        self.show_info(follow.to_id)

    def show_follows(self) -> None:
        """Shows a list of channels that the user follows."""
        follows = {user.to_name: user for user in self.user_follows}
        follows_names = list(follows.keys())
        selected = self.menu.show_items(self._executor, follows_names, prompt="'twitch follows:'", back=True)

        if not selected:
            sys.exit(1)

        if selected == self.menu.back:
            self.show_menu()

        selected = self.clean_channel_name(selected)

        if selected not in follows_names:
            log.warning("Option %s not found.", C.red(selected))
            self.menu.show_items(
                self._executor, [f"Channel '{selected}' not found."], prompt="'twitch follows:'", back=True
            )
            self.show_follows()

        follow = follows[selected]

        self.show_info(follow.to_id)

    def show_follows_videos(self, channel: BroadcasterInfo) -> None:
        """Shows a list of videos for the specified channel."""
        channel_videos = self.twitch.channels.videos(user_id=channel.broadcaster_id)

        videos_dict = {
            f"{self.menu.unicode.BULLET_ICON} {video.title} | {video.duration} (views: {video.view_count})": video
            for video in channel_videos
        }

        if not videos_dict:
            log.warning("No available videos from followed channel: %s", C.info(channel.broadcaster_name))
            self.menu.show_items(
                self._executor,
                ["No available videos from followed channel"],
                prompt=f"'{channel.broadcaster_name} videos:'",
                back=True,
            )
            self.show_info(channel.broadcaster_id)

        selected = self.menu.show_items(
            self._executor,
            list(videos_dict.keys()),
            prompt=f"'{channel.broadcaster_name} videos:'",
            back=True,
        )

        if not selected:
            sys.exit(1)

        if selected == self.menu.back:
            self.show_info(channel.broadcaster_id)
        else:
            video = videos_dict[selected]
            self.load_stream_selected(video.url)
            self.show_follows_videos(channel)

    def show_menu(self) -> None:
        """
        Displays the main menu of the app, with options to view online channels
        and channels that the user follows.
        """
        menu_options: MenuOptions = {
            f"{self.menu.unicode.BULLET_ICON} All follows": self.show_follows,
            f"{self.menu.unicode.BULLET_ICON} Live followed": self.show_online_follows,
        }

        menu = functools.partial(self.menu.show_items)
        options_keys = list(menu_options.keys())
        option_selected = menu(self._executor, options_keys)

        if not option_selected:
            sys.exit(1)

        if option_selected not in list(options_keys):
            log.warning("Option %s not found.", C.red(option_selected))
            self.menu.show_items(
                self._executor, [f"Option '{option_selected}' selected not found."], prompt="twitch:", back=True
            )
            self.show_menu()

        run_option = menu_options[option_selected]
        selected = run_option()

        if selected == self.menu.back:
            self.show_menu()

        sys.exit(0)

    def show_info(self, user_id: str) -> None:
        """
        Shows information about a specific channel, including the channel's name, status, game being played,
        and a menu to view the channel's videos or schedule.

        Args:
        channel_id (int): The ID of the channel to display information for.

        Returns:
        None: The selected option is executed.
        """
        channel = self.twitch.channels.information(user_id)

        menu_info = []
        category = f"Category: {channel.game_name}"
        menu_info.append(category)
        menu_info.append("-" * len(category))
        menu_info.append(f"Last Stream: {channel.title}")
        menu_info.append("Videos: Get videos")
        menu_info.append("Clips: Get clips")

        selected = self.menu.show_items(
            self._executor,
            menu_info,
            prompt=f"'{channel.broadcaster_name} info:'",
            back=True,
        )

        if selected is None:
            sys.exit(1)

        if selected == self.menu.back:
            self.show_follows()

        if selected.startswith("Clips"):
            self.show_clips(channel)

        if selected.startswith("Videos"):
            self.show_follows_videos(channel)

        if selected.startswith("Last"):
            print("Selected:", selected)

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
            f"{self.menu.unicode.BULLET_ICON} {idx} {c.title} | creator: {c.creator_name} ({c.view_count} views)": c
            for idx, c in enumerate(clips)
        }

        if not clips_dict:
            log.warning("No available %s from followed channel: %s", C.green("clips"), C.info(channel.broadcaster_name))
            self.menu.show_items(
                self._executor,
                ["No available clips from followed channel"],
                prompt=f"'{channel.broadcaster_name} clips:'",
                back=True,
            )
            self.show_info(channel.broadcaster_id)

        option_selected = self.menu.show_items(
            self._executor,
            list(clips_dict.keys()),
            prompt=f"'{channel.broadcaster_name} clips:'",
            back=True,
        )

        if not option_selected:
            sys.exit(1)

        if option_selected == self.menu.back:
            self.show_info(channel.broadcaster_id)
        else:
            clip = clips_dict[option_selected]
            self.load_clip_selected(clip)
            self.show_clips(channel, list(clips_dict.values()))
