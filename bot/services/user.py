from enum import Enum
from typing import Union

from repositories.students import StudentsModelRepository
from repositories.workers import WorkersRepository
from .base import BaseService


class UserType(Enum):
    WORKER = "W"
    STUDENT = "S"
    UNKNOWN = "U"


class UserService(BaseService):
    default_workers_repository = WorkersRepository()
    default_students_repository = StudentsModelRepository()

    def __init__(self, workers_repostitory: WorkersRepository = None,
                 students_repository: StudentsModelRepository = None):
        self._workers_repository = (workers_repostitory or
                                    self.default_workers_repository)
        self._students_repository = (students_repository or
                                     self.default_students_repository)

    async def get_user(self, telegram_id: int) -> tuple[
        UserType, Union["Worker", "Student",  None]
    ]:
        try:
            worker = await self._workers_repository.get(pk=telegram_id)

            if not worker:
                raise ValueError

            return UserType.WORKER, worker
        except:
            try:
                student = await self._students_repository.get_by_telegram(
                    telegram_id=telegram_id
                )

                if not student:
                    print(f"STUDENT NOT FOUND: {telegram_id} - {await self._students_repository.get_all()}")

                if not student:
                    raise ValueError

                return UserType.STUDENT, student
            except:
                return UserType.UNKNOWN, None
