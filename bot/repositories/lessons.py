from .base import DefaultModelRepository, BaseModelRepository

from models.lesson import Lesson

from .base import DefaultModelRepository, BaseModelRepository


class LessonsModelRepository(DefaultModelRepository):
    _model = Lesson

    @BaseModelRepository._provide_db_conn()
    async def create(self, lesson_data: Lesson,
                     session: AsyncSession) -> Lesson:
        return await super().create(session=session, data=lesson_data)
