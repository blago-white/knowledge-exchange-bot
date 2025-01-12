import datetime
import typing

from .base import BaseService

from models.lesson import Subject, Lesson
from models.worker import Worker
from repositories.workers import WorkersRepository
from repositories.lessons import LessonsModelRepository
from repositories.base import BaseModelRepository


class WorkersService(BaseService):
    workers_model_repository = WorkersRepository()
    lessons_model_repository = LessonsModelRepository()

    _worker_id: int | None

    def __init__(self, worker_id: int = None,
                 workers_repository: WorkersRepository = None,
                 lessons_repository: LessonsModelRepository = None):
        self._worker_id = worker_id
        self._workers_repository = (workers_repository or
                                    self.workers_model_repository)
        self._lessons_repository = (lessons_repository or
                                    self.lessons_model_repository)

    async def get_selled_students_count(self) -> int:
        worker: Worker = await self._workers_repository.get(
            pk=self._worker_id,
            exclude_related_cols=set(
                self._workers_repository.relation_fields_mappings
            ) ^ {Worker.outcome_sell_offers}
        )

        return len(worker.outcome_sell_offers)

    @BaseModelRepository.provide_db_conn()
    async def get_week_profit(self, session) -> int:
        worker: Worker = await self._workers_repository.get(
            session=session,
            pk=self._worker_id,
        )

        profit_for_week = await self._lessons_repository.get_week_lessons_pay(
            *(s.id for s in worker.subjects)
        )

        return profit_for_week

    @staticmethod
    def _get_week_borders() -> tuple[int, int]:
        today = datetime.datetime.today()
        start = today - datetime.timedelta(days=today.weekday())

        return (
            start.timestamp(),
            (start + datetime.timedelta(days=6)).timestamp()
        )
