import datetime

from models.lesson import Subject, Lesson
from models.worker import Worker
from repositories.base import BaseModelRepository
from repositories.lessons import LessonsModelRepository
from repositories.workers import WorkersRepository
from .base import BaseModelService


class WorkersService(BaseModelService):
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

    @property
    def repository(self):
        return self._workers_repository

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

    async def sell_student(self, buyer_worker_id: int, subject_id: int):
        ...

    async def get_selled_student_lessons(
            self, subject_id: int
    ) -> list["Lesson"]:
        ...

    async def get_selled_student_status(self, subject_id: int) -> "StudentSellOffer":
        ...

    async def get_active_subjects(self) -> list["Subject"]:
        ...

    async def add_message_to_student(self, message: "Message", subject_id: int):
        ...

    async def get_dialog(self, subject_id: int):
        ...
