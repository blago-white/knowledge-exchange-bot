from typing import Iterable

from sqlalchemy import select, update
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, Mapped

from models import DBSessionAccesObject

Model = object


class BaseModelRepository:
    _model: object

    @staticmethod
    def provide_db_conn(session: Connection = None, make_commit: bool = False):
        def wrapper(func):
            async def wrapped(*args, **kwargs):
                use_session = session or DBSessionAccesObject().sessionmaker

                if not ("session" in kwargs):
                    async with use_session() as active_session:
                        kwargs |= {"session": active_session}

                        result = await func(*args, **kwargs)
                else:
                    result = await func(*args, **kwargs)

                if make_commit:
                    await active_session.commit()

                return result
            return wrapped
        return wrapper


class DefaultModelRepository(BaseModelRepository):
    @BaseModelRepository.provide_db_conn()
    async def get_all(self, session: AsyncSession) -> list[Model]:
        return (await session.execute(select(self._model))).scalars().all()

    @BaseModelRepository.provide_db_conn()
    async def get(self, session: AsyncSession, pk: int,
                  exclude_related_cols: Iterable[Mapped] = tuple()) -> Model:
        return (await session.execute(select(self._model).options(
            *[lazyload(e) for e in exclude_related_cols]
        ).filter_by(
            id=pk
        ))).unique().scalars().one_or_none()

    @BaseModelRepository.provide_db_conn()
    async def create(self, data: object,
                     session: AsyncSession) -> Model:
        session.add(data)

        await session.commit()

        await session.refresh(data)

        return data

    @BaseModelRepository.provide_db_conn()
    async def update(self, session: AsyncSession,
                     pk: int,
                     **change_params: dict[str, object]) -> Model:
        for k in change_params.keys():
            try:
                getattr(self, f"_validate_{k}")(change_params[k])
            except AttributeError:
                pass

        await session.execute(
            update(self._model).where(self._model.id == pk).values(
                **change_params
            )
        )

        await session.commit()

        return await self.get(session=session, pk=pk)

