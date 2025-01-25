from enum import Enum

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
        UserType, "Worker" | "Student" | None
    ]:
        try:
            return UserType.WORKER, await self._workers_repository.get(
                pk=telegram_id
            )
        except:
            try:
                return UserType.STUDENT, await self._students_repository.get(
                    pk=telegram_id
                )
            except:
                return UserType.UNKNOWN, None
