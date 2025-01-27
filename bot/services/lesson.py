from models.lesson import Lesson
from repositories.lessons import LessonsModelRepository
from .base import BaseModelService


class LessonsService(BaseModelService):
    lessons_model_repository = LessonsModelRepository()

    _lesson_id: int | None

    def __init__(self, lesson_id: int = None,
                 lessons_repository: LessonsModelRepository = None):
        self._lesson_id = lesson_id
        self._lessons_repository = (lessons_repository or
                                    self.lessons_model_repository)

    @property
    def repository(self):
        return self._lessons_repository

        # worker: Worker = await self.get(
        #     session=session,
        #     pk=self._worker_id,
        # )
        #
        # profit_for_week = await self._lessons_repository.get_week_lessons_pay(
        #     *(s.id for s in worker.subjects)
        # )
        #
        # return profit_for_week
