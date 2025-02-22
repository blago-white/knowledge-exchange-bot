from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseModelService

from models.student import Student
from models.worker import Worker
from models.deposits import Deposit

from repositories.base import BaseModelRepository
from repositories.students import StudentsModelRepository
from repositories.workers import WorkersRepository
from repositories.deposits import DepositsModelRepository


class DepositsService(BaseModelService):
    _repository = DepositsModelRepository()
    _students_repository = StudentsModelRepository()
    _workers_repository = WorkersRepository()

    @BaseModelRepository.provide_db_conn()
    async def set_success(self, user: Student | Worker,
                          deposit: Deposit,
                          session: AsyncSession):
        if type(user) is Student:
            await self._students_repository.update(
                session=session,
                pk=user.id,
                balance=user.balance + deposit.amount,
            )

            telegram_id = user.telegram_id
        else:
            await self._workers_repository.update(
                session=session,
                pk=user.id,
                balance=user.balance + deposit.amount
            )

            telegram_id = user.id

        await self._repository.set_success(session=session,
                                           telegram_id=telegram_id)

        await session.commit()
