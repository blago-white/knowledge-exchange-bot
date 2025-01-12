from sqlalchemy.ext.asyncio import AsyncSession

from models.student import Student

from .base import DefaultModelRepository, BaseModelRepository


class StudentsModelRepository(DefaultModelRepository):
    _model = Student

    @BaseModelRepository.provide_db_conn()
    async def create(self, student_data: Student,
                     session: AsyncSession) -> Student:
        return await super().create(session=session, data=student_data)
