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
