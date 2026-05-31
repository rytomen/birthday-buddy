import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base


def make_engine(database_url=None):
    if database_url is None:
        database_url = os.environ.get("DATABASE_URL", "sqlite:///birthdays.db")
    kwargs = {"future": True}
    if database_url in ("sqlite:///:memory:", "sqlite://"):
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


def init_db(engine):
    Base.metadata.create_all(engine)


def make_session_factory(engine):
    return sessionmaker(bind=engine, future=True)
