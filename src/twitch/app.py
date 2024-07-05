# app.py
from __future__ import annotations

import logging
import typing
import webbrowser
from dataclasses import asdict
from typing import Any
from typing import Callable
from typing import Mapping
from typing import NamedTuple
from typing import Protocol

from twitch import clipboard
from twitch import format
from twitch import player
from twitch._exceptions import ItemNotPlaylableError
from twitch.constants import SEPARATOR
from twitch.constants import UserCancel
from twitch.constants import UserConfirms
from twitch.datatypes import TwitchChannel
from twitch.datatypes import TwitchContent
from twitch.models.category import Category

if typing.TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface
    from pyselector.key_manager import Keybind
    from twitch.client import TwitchFetcher

log = logging.getLogger(__name__)

# TODO:
# - [X] get player inside TwitchApp.play() method
# - [ ] find a better way to show items in loop
#       - example: show_top_streams and hit group_by_games


class Keys(NamedTuple):
    group_by_categories: str
    show_information: str
    open_chat: str
    show_keys: str
    search_by_game: str
    search_by_query: str
    # Content
    top_streams: str
    top_games: str
    videos: str
    clips: str


TwitchData = tuple[Mapping[str, TwitchChannel | TwitchContent], str]


class TwitchPlayableContent(Protocol):
    url: str
    playable: bool


class TwitchApp:
    def __init__(self, fetcher: TwitchFetcher, menu: MenuInterface, player_conf: bool, keys: Keys):
        self.fetch = fetcher
        self.menu = menu
        self.player_conf = player_conf
        self.keys = keys

    async def show_all_streams(self, **kwargs: dict[str, Any]) -> int:
        # FIX: Is this loop necessary?
        km = self.menu.keybind
        items, mesg = await self.get_channels_and_streams()
        currentkeys = km.list_keys.copy()
        while True:
            km.unregister_all()
            km.register_all(currentkeys)
            item, keycode = self.select(items=items, mesg=mesg)

            # If user hit escape
            if not item:
                return UserCancel(1)

            # FIX: workaround for user input not in the list
            if not hasattr(item, 'playable'):
                err = f'{item!r} is not playable'
                raise ItemNotPlaylableError(err)

            # Show offline channel's videos if selected item is offline
            if not item.playable and keycode == UserConfirms(0):
                return await self.show_videos(item=item)

            # If user selected a item
            if keycode == UserConfirms(0):
                break

            # If user used a keybind
            if keycode not in (UserConfirms(0), UserCancel(1)):
                k = self.get_key_by_code(keycode)
                return await k.action(item=item, keybind=k, items=items)

        return self.play(name=item.name, url=item.url)

    async def show_videos(self, **kwargs: dict[str, TwitchChannel]) -> int:
        item: TwitchChannel = kwargs.pop('item')
        self.menu.keybind.unregister_all()
        videos, mesg = await self.get_channel_videos(item=item)
        return await self.show_and_play(items=videos, mesg=mesg)

    async def show_clips(self, **kwargs: dict[str, TwitchChannel]) -> int:
        item: TwitchChannel = kwargs.pop('item')
        self.menu.keybind.unregister_all()
        clips, mesg = await self.get_channel_clips(item=item)
        return await self.show_and_play(items=clips, mesg=mesg)

    async def show_group_by_categories(self, **kwargs: dict[str, TwitchChannel]) -> int:
        categories: dict[str, Category] = {}
        items: dict[str, TwitchChannel] = kwargs.get('items', {})

        for chan in items.values():
            if not chan.live:
                continue
            category = categories.setdefault(
                chan.game_name,
                Category(name=chan.game_name, channels={}, markup=self.markup),
            )
            category.channels[chan.name] = chan

        categories_sorted = sorted(categories.items(), key=lambda x: x[1].total_viewers(), reverse=True)
        mesg = f'> Showing ({len(categories)}) <games>'
        category, keycode = self.select(items=dict(categories_sorted), mesg=mesg)
        if not category:
            return 1

        mesg = f'> Showing ({len(category.channels)}) <channels> from <{category.name}> category'
        return await self.show_and_play(category.channels, mesg=mesg)

    async def show_keybinds(self, **kwargs: dict[str, TwitchChannel]) -> int:
        item: TwitchChannel = kwargs.pop('item')
        key: Keybind = kwargs.pop('keybind')
        key.toggle()
        items: dict[str, str] = {}
        keybinds: dict[int, Keybind] = self.menu.keybind.keys
        for key in keybinds.values():
            items[key.bind] = key
        mesg = f'> Showing ({len(keybinds)}) <keybinds>\n> item selected: <{item.name}>'

        while True:
            keybind, keycode = self.select(items=items, mesg=mesg)
            if keycode == UserCancel(1):
                return UserCancel(1)
            if keycode != 0:
                keybind = self.get_key_by_code(keycode)
            await keybind.action(**kwargs, keybind=keybind, item=item)
        return 1

    async def show_and_play(self, items: Mapping[str, TwitchPlayableContent], mesg: str = '') -> int:
        # FIX: experimental
        while True:
            item, keycode = self.select(items=items, mesg=mesg)
            if keycode == UserConfirms(0):
                break
            if not item or keycode == UserCancel(1):
                return UserCancel(1)
            if keycode not in (UserConfirms(0), UserCancel(1)):
                await self.get_key_by_code(keycode).action(items=items, item=item)

        if not hasattr(item, 'playable') or not item.playable:
            err = f"item='{item.name}' is not playable"
            raise ItemNotPlaylableError(err)

        return self.play(name=item.name, url=item.url)

    async def show_by_query(self, **kwargs) -> int:
        query: str | None = kwargs.get('query')
        if not query:
            query = self.get_user_input(mesg='Search <channels> by query', prompt='TwitchChannel>')

        if not query:
            log.warn('query search cancelled by user')
            return 1

        data = await self.fetch.channels_by_query(query, live_only=False)
        items = {c.id: c for c in data}
        self.toggle_content_keybinds()
        mesg = f'> Showing ({len(items)}) <channels> by query: "{query}"'
        return await self.show_and_play(items=items, mesg=mesg)

    async def show_by_game(self, **kwargs) -> int:
        game = kwargs.get('game')
        if not game:
            game = self.get_user_input(mesg='Search <games> or <categories>', prompt='TwitchGame>')

        if not game:
            log.warn('query search cancelled by user')
            return 1

        data = await self.fetch.games_by_query(game)
        games = {g.id: g for g in data}
        selected, _ = self.select(games, mesg=f'> Showing ({len(games)}) <games> or <categories>')
        if not selected:
            return 1

        self.toggle_content_keybinds()
        data = await self.fetch.streams_by_game_id(selected.id)
        streams = list(data)
        if not streams:
            self.select(items={}, mesg='> No <streams> found')
            return 1

        mesg = f'> Showing ({len(streams)}) <streams> from <{selected.name}> game'
        return await self.show_and_play({s.id: s for s in streams}, mesg=mesg)

    async def show_top_streams(self, **kwargs) -> int:
        kgames = self.get_key_by_bind(self.keys.group_by_categories)
        self.toggle_content_keybinds()
        self.menu.keybind.register(kgames)
        data = await self.fetch.top_streams()
        streams = {s.name: s for s in data}
        mesg = f'> Showing ({len(streams)}) top streams'
        return await self.show_and_play(items=streams, mesg=mesg)

    async def show_item_info(self, **kwargs) -> int:
        self.menu.keybind.unregister_all()
        item: TwitchContent | TwitchChannel = kwargs['item']
        item.title = format.sanitize(item.title)
        item_dict = asdict(item)
        formatted_item = format.stringify(item_dict, sep=SEPARATOR)
        formatted_item.insert(0, f"{'url':<18}{SEPARATOR}\t{item.url:<30}")
        selected, keycode = self.menu.prompt(
            items=formatted_item,
            mesg=f'> item <{item.name}> information\n> Hit enter to copy',
        )
        if selected is None:
            return keycode

        selected = selected.split(SEPARATOR, maxsplit=1)[1].strip()
        clipboard.copy(selected)
        return keycode

    async def show_top_games(self, **kwargs) -> int:
        log.info('processing top games')
        categories = await self.fetch.top_games_with_streams()
        nviewers: int = sum([c.total_viewers() for c in categories.values()])
        nchannels: int = sum([c.channels_live() for c in categories.values()])
        km = self.menu.keybind
        keybinds = km.get_by_bind_list([self.keys.clips, self.keys.videos])

        # Top games and top streams loop
        while True:
            mesg = f'> Showing {len(categories)} top categories '
            mesg += f'({nchannels} streams and {format.number(nviewers)} viewers)'
            km.unregister_all()
            cat, keycode = self.select(items=categories, mesg=mesg)
            if not cat:
                return UserCancel(1)

            # Toggle keybind hidden property
            [keybind.toggle() for keybind in keybinds]

            km.register_all(keybinds)
            mesg = f'> Showing ({len(cat.channels)}) streams from <{cat.name}> category'
            item, keycode = self.select(items=cat.channels, mesg=mesg)

            # If user hit escape
            if not item:
                continue

            # If user selected a item
            if keycode == UserConfirms(0):
                break

            # If user used a keybind
            if keycode not in (UserConfirms(0), UserCancel(1)):
                keybind = self.get_key_by_code(keycode)
                await keybind.action(item=item)

        return self.play(name=item.name, url=item.url)

    async def get_channels_and_streams(self) -> TwitchData:
        data = await self.fetch.channels_and_streams()
        if self.fetch.online == 0:
            return data, f'> No streams online found from {len(data)} channels'
        return data, f'> Showing ({self.fetch.online}) streams from {len(data)} channels'

    async def get_channel_clips(self, **kwargs) -> TwitchData:
        item: TwitchChannel = kwargs.pop('item')
        log.info("processing user='%s' clips", item.name)
        clips = sorted(
            await self.fetch.clips(user_id=item.user_id),
            key=lambda c: c.created_at,
            reverse=True,
        )
        data = {c.key: c for c in clips}
        if len(data) == 0:
            return data, f'> No clips found from <{item.name}> channel'
        return data, f'> Showing ({len(data)}) clips from <{item.name}> channel'

    async def get_channel_videos(self, **kwargs) -> TwitchData:
        item = kwargs.pop('item')
        data = {v.key: v for v in await self.fetch.videos(user_id=item.user_id)}
        if len(data) == 0:
            return data, f'> No videos found from <{item.name}> channel'
        return data, f'> Showing ({len(data)}) videos from <{item.name}> channel'

    def get_key_by_code(self, keycode: int) -> Keybind:
        return self.menu.keybind.get_by_code(keycode)

    def get_key_by_bind(self, bind: str) -> Keybind:
        return self.menu.keybind.get_by_bind(bind)

    def get_user_input(self, mesg: str = '', prompt: str = 'Query>') -> str:
        self.menu.keybind.toggle_hidden()
        user_input, _ = self.menu.prompt(
            items=[],
            mesg=mesg,
            prompt=prompt,
            print_query=True,
            markup=self.markup,
        )
        self.menu.keybind.toggle_hidden(restore=True)
        if not user_input:
            return ''
        return user_input.strip()

    def toggle_content_keybinds(self) -> None:
        km = self.menu.keybind
        content_keys = km.get_by_bind_list(
            [
                self.keys.show_information,
                self.keys.videos,
                self.keys.clips,
            ]
        )
        km.unregister_all()
        for k in content_keys:
            k.toggle()
        km.register_all(content_keys, exist_ok=True)

    def select(
        self,
        items: Mapping[str, Any],
        mesg: str = '',
        preprocessor: Callable[..., Any] | None = None,
    ) -> tuple[Any, int]:
        if not items:
            self.menu.prompt(items=['err: no items'], mesg=mesg, markup=False)
            return None, UserCancel(1)

        item, keycode = self.menu.prompt(
            items=list(items.values()),
            mesg=mesg,
            markup=self.markup,
            preprocessor=preprocessor,
        )

        return item, keycode

    async def multi_selection(self, **kwargs) -> None:
        raise NotImplementedError

    def play(self, name: str, url: str) -> int:
        # https://github.com/jaseg/python-mpv/issues/126
        log.info(f'playing {name!r} {url!r}')
        p = player.get(with_config=self.player_conf, name=name)
        p.play(url)
        p.wait_for_playback()
        del p
        return 0

    async def open_chat(self, **kwargs) -> int:
        item = kwargs.pop('item')
        log.debug(f'opening chat for {item.name}')
        webbrowser.open_new_tab(item.chat)
        return 0

    async def quit(self, **kwargs) -> int:
        keycode = kwargs.get('keycode', 0)
        await self.fetch.close()
        log.debug('terminated by user')
        return keycode

    @property
    def markup(self) -> bool:
        return self.fetch.markup
