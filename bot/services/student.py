from models.student import Student
from repositories.students import StudentsModelRepository

from .transfer.student import StudentInitializingData
from .base import BaseModelService


class StudentsService(BaseModelService):
    _repository = StudentsModelRepository()
    _student_id: int | None
    _telegram_id: int | None

    @property
    def repository(self) -> StudentsModelRepository:
        return self._repository

    @property
    def telegram_id(self):
        return self._telegram_id

    @property
    def student_id(self):
        return self._student_id

    @telegram_id.setter
    def telegram_id(self, tid: int):
        self._telegram_id = tid

    @student_id.setter
    def student_id(self, sid: int):
        self._student_id = sid

    async def initialize(self, student_data: StudentInitializingData) -> int:
        result = await self._repository.create(student_data=Student(
            **student_data.__dict__
        ))

        return result.id

    async def connect_student_telegram(self):
        if not (self._telegram_id and self._student_id):
            raise ValueError("Cannot connect tg id, `_telegram_id` and "
                             "`_student_id` must be setted")

        await self._repository.update(
            pk=self._student_id,
            telegram_id=self._telegram_id
        )

        return True
