# crud.py

from collections.abc import Iterable
from typing import Optional

from twitch import datatypes
from twitch.database.db import Base
from twitch.database.db import SessionLocal
from twitch.database.db import engine
from twitch.database.models import TwitchChannelsDB
from twitch.utils import logger
from twitch.utils.colors import Color as C

log = logger.get_logger(__name__)


class TwitchDatabase:
    def __init__(self) -> None:
        self.db = SessionLocal()

        self._init()

    def _init(self) -> None:
        Base.metadata.create_all(bind=engine)

    @property
    def channels(self) -> Iterable[TwitchChannelsDB]:
        return self.all_channels()

    def all_channels(self, skip: int = 0, limit: int = 100) -> Iterable[TwitchChannelsDB]:
        return self.db.query(TwitchChannelsDB).offset(skip).limit(limit).all()

    def create_channel(self, data: datatypes.TwitchChannel) -> TwitchChannelsDB:
        db_item = TwitchChannelsDB(
            user_id=data.user_id,
            user_login=data.user_login,
            user_name=data.user_name,
            game_id=data.game_id,
            game_name=data.game_name,
            title=data.title,
            thumbnail_url=data.thumbnail_url,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_channels(self, data: datatypes.TwitchStreams) -> Optional[TwitchChannelsDB]:
        for channel in data:
            if not self.channel_exists(int(channel.user_id)):
                new_channel = datatypes.TwitchChannel(
                    user_id=int(channel.user_id),
                    user_login=channel.user_login,
                    user_name=channel.user_name,
                    game_id=int(channel.game_id),
                    game_name=channel.game_name,
                    title=channel.title,
                    thumbnail_url=channel.thumbnail_url,
                )
                log.info("%s channel %s", C.green("Saving"), C.cyan(channel.user_login))
                return self.create_channel(new_channel)

        log.info(C.info("No new channels added"))
        return None

    def get_channel_by_id(self, channel_id: int) -> datatypes.TwitchChannel:
        data = self.db.query(TwitchChannelsDB).get(channel_id)
        return data

    def channel_exists(self, channel_id: int) -> bool:
        return bool(self.db.query(TwitchChannelsDB).get(channel_id))

    def delete_channel(self, channel_id: int) -> None:
        channel = self.get_channel_by_id(channel_id)
        if not channel:
            log.info("Channel with ID:%s %s", C.info(str(channel_id)), C.red("not found"))
            return None

        self.db.delete(channel)
        self.db.commit()

        log.info("Channel %s deleted", C.red(channel.user_name))
        return None

    def count_channels(self) -> int:
        return self.db.query(TwitchChannelsDB).count()

    def get_channel_by_game(self, name: str) -> Optional[Iterable[TwitchChannelsDB]]:
        channels = self.db.query(TwitchChannelsDB).filter_by(game_name=name).all()
        if not channels:
            log.info("Channel %s %s", C.info(str(name)), C.red("not found"))
            return None
        return channels

    def get_channel_by_name(self, name: str) -> Optional[TwitchChannelsDB]:
        channel = self.db.query(TwitchChannelsDB).filter_by(user_login=name).first()
        if not channel:
            return None
        return channel
