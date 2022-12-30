# models.py

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from twitch.database.db import Base


class TwitchChannelsDB(Base):
    __tablename__ = "channels"
    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_login = Column(String(120), nullable=False)
    user_name = Column(String(120), nullable=False)
    game_id = Column(Integer, nullable=False)
    game_name = Column(String(120), nullable=False)
    title = Column(String(256))
    thumbnail_url = Column(String(256))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.user_id}@{self.user_login}:{self.game_name})"
