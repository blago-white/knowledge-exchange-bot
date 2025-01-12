import datetime
import typing

from .base import BaseService

from models.lesson import Subject, Lesson
from models.worker import Worker
from repositories.workers import WorkersRepository
from repositories.lessons import LessonsModelRepository
from repositories.base import BaseModelRepository


class WorkersService(BaseService):
    lessons_model_repository = LessonsModelRepository()

    _lesson_id: int | None

    def __init__(self, lesson_id: int = None,
                 lessons_repository: LessonsModelRepository = None):
        self._lesson_id = lesson_id
        self._lessons_repository = (lessons_repository or
                                    self.lessons_model_repository)

    async def bulk_add_lessons(self, lesson: Lesson, count: int) -> int:
        self._lessons_repository.create(lesson_data=Lesson)

        # worker: Worker = await self..get(
        #     session=session,
        #     pk=self._worker_id,
        # )
        #
        # profit_for_week = await self._lessons_repository.get_week_lessons_pay(
        #     *(s.id for s in worker.subjects)
        # )
        #
        # return profit_for_week
