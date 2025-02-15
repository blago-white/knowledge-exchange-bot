from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, select, or_

from models.student import Student
from models.lesson import Subject
from .base import DefaultModelRepository, BaseModelRepository


class SubjectsModelRepository(DefaultModelRepository):
    _model = Subject

    @BaseModelRepository.provide_db_conn()
    async def create(self, subject_data: Subject,
                     session: AsyncSession) -> Subject:
        return await super().create(session=session, data=subject_data)

    @BaseModelRepository.provide_db_conn()
    async def worker_has_subject(self, worker_id: int,
                                 subject_id: int,
                                 session: AsyncSession) -> bool:
        return await session.scalar(select(
            self._model.id,
            self._model.worker_id,
        ).filter_by(
            worker_id=worker_id,
            id=subject_id,
        ))

    @BaseModelRepository.provide_db_conn()
    async def get_all_for_worker(self, worker_id: int,
                                 session: AsyncSession) -> list[Subject]:
        return list((await session.execute(select(self._model).filter_by(
            worker_id=worker_id
        ))).scalars())

    @BaseModelRepository.provide_db_conn()
    async def get_all(self, session: AsyncSession,
                      user_id: int = None):
        query = select(self._model)

        if user_id:
            query = query.filter(or_(
                self._model.worker_id == user_id,
                Student.telegram_id == user_id
            ))

        return list((await session.execute(query)).unique().scalars())
