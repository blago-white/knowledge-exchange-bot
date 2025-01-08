from sqlalchemy.ext.asyncio import AsyncSession

from models.lesson import Subject

from .base import DefaultModelRepository, BaseModelRepository


class SubjectsModelRepository(DefaultModelRepository):
    _model = Subject

    @BaseModelRepository._provide_db_conn()
    async def create(self, subject_data: Subject,
                     session: AsyncSession) -> Subject:
        return await super().create(session=session, data=subject_data)
