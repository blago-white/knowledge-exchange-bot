from .base import DefaultModelRepository, BaseModelRepository

from bot.models.student import Student


class LessonsModelRepository(DefaultModelRepository):
    _model = Student

    @BaseModelRepository._provide_db_conn()
    async def create(self, student_data: Student,
                     session: AsyncSession) -> WorkerModel:
        return await super().create(session=session, data=student_data)
