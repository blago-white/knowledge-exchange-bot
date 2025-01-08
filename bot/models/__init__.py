from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import (async_sessionmaker,
                                    AsyncSession,
                                    create_async_engine)

from . import dialog, course, lesson, student, worker


__all__ = ["DBSessionAccesObject"]


class DBSessionAccesObject:
    _session_maker: Connection = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBSessionAccesObject, cls).__new__(cls)
        return cls.instance

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if not self._session_maker:
            print("Sessionmaker not configured")
            raise ValueError("Sessionmaker not configured")
        return self._session_maker

    @sessionmaker.setter
    def sessionmaker(self, sessionmaker: async_sessionmaker[AsyncSession]):
        print(f"CONFIGURED: {sessionmaker=}")
        if not sessionmaker:
            raise ValueError("Not correct sessionmaker val")

        self._session_maker = sessionmaker
