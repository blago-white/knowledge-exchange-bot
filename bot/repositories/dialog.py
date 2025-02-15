from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import DefaultModelRepository, Model
from models.dialog import Message


class DialogRepository(DefaultModelRepository):
    _model = Message

    @DefaultModelRepository.provide_db_conn()
    async def get_all_for_subject(self, session: AsyncSession, subject_id: int):
        return (await session.execute(
            select(self._model).filter_by(subject_id=subject_id)
        )).scalars()

    @DefaultModelRepository.provide_db_conn()
    async def get_previews_for_subjects(
            self, session: AsyncSession,
            subjects_ids: list[int]
    ):
        return list((await session.execute(
            select(self._model).filter(
                Message.subject_id.in_(subjects_ids)
            ).order_by(Message.subject_id).distinct(Message.subject_id)
        )).scalars())
