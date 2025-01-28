from models.lesson import Lesson, Subject
from repositories.lessons import LessonsModelRepository
from repositories.subjects import SubjectsModelRepository

from .transfer.subjects import SubjectsInitializingData
from .base import BaseModelService


class LessonsService(BaseModelService):
    _repository = LessonsModelRepository()

    _lesson_id: int | None

    def __init__(self, *args,
                 lesson_id: int = None,
                 lessons_repository: LessonsModelRepository = None,
                 **kwargs):
        self._lesson_id = lesson_id
        self._repository = lessons_repository or self._repository

        super.__init__(*args, **kwargs)

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


class SubjectsService(BaseModelService):
    _repository = SubjectsModelRepository()

    _subject_id: int = None
    _subject_title: str | None

    def __init__(self, *args,
                 subject_title: str = None,
                 subjects_repository: SubjectsModelRepository = None,
                 **kwargs):
        self._subject_title = subject_title
        self._repository = subjects_repository or self._repository

        super().__init__(*args, **kwargs)

    @property
    def repository(self):
        return self._repository

    @property
    def subject_id(self):
        return self._subject_id

    @subject_id.setter
    def subject_id(self, subject_id):
        self._subject_id = subject_id

    async def retrieve(self, worker_id: int):
        if await self.repository.worker_has_subject(
            subject_id=self._subject_id, worker_id=worker_id
        ):
            return await self.repository.get(pk=self._subject_id)

        raise ValueError("You is not owner!")

    async def initialize(self, data: SubjectsInitializingData) -> int:
        return (await self._repository.create(
            subject_data=Subject(**data.__dict__)
        )).id

    async def get_lessons(self, worker_id: int):
        if await self.repository.worker_has_subject(
            subject_id=self._subject_id, worker_id=worker_id
        ):
            return (await self.repository.get(
                pk=self._subject_id,
                exclude_related_cols=[
                    Subject.sell_offers,
                    Subject.messages,
                    Subject.student,
                ]
            )).lessons

        raise ValueError("You is not owner!")
