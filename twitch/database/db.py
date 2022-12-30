# database.py

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_NAME = "twitch_channels.db"
DATABASE_URI = BASE_DIR / DATABASE_NAME

engine = create_engine(f"sqlite:///{DATABASE_URI}", connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
