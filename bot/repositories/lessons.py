from .base import DefaultModelRepository, BaseModelRepository

from bot.models.lesson import Lesson


class LessonsModelRepository(DefaultModelRepository):
    _model = Lesson

    @BaseModelRepository._provide_db_conn()
    async def create(self, lesson_data: Lesson,
                     session: AsyncSession) -> WorkerModel:
        return await super().create(session=session, data=lesson_data)
