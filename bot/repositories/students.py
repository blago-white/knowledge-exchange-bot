from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from models.student import Student, StudentSellOffer
from .base import DefaultModelRepository, BaseModelRepository


class StudentsModelRepository(DefaultModelRepository):
    _model = Student

    @BaseModelRepository.provide_db_conn()
    async def create(self, student_data: Student,
                     session: AsyncSession) -> Student:
        return await super().create(session=session, data=student_data)

    @BaseModelRepository.provide_db_conn()
    async def drop_unauthorized(
            self, student_id: int,
            session: AsyncSession
    ) -> Student:
        await session.execute(delete(self._model).filter_by(
            pk=student_id,
            telegram_id=None
        ))

        await session.commit()

        return True


class StudentsSellOffersModelRepository(DefaultModelRepository):
    _model = StudentSellOffer

    @BaseModelRepository.provide_db_conn()
    async def get(self, subject_id: int,
                  session: AsyncSession) -> StudentSellOffer:
        return (await session.execute(select(self._model).filter_by(
            subject_id=subject_id
        ))).scalars().one_or_none()

    @BaseModelRepository.provide_db_conn()
    async def get_total_revenue(self, worker_id: int, session: AsyncSession):
        return (
            await session.execute(
                select(
                    func.sum(self._model.paid_sum)
                ).filter_by(
                    seller_id=worker_id
                )
            )
        ).scalar() or 0

    @BaseModelRepository.provide_db_conn()
    async def get_selled_count(self, worker_id: int, session: AsyncSession) -> int:
        return (
            await session.execute(
                select(
                    func.count(self._model.id)
                ).filter_by(seller_id=worker_id)
            )
        ).scalar() or 0

    @BaseModelRepository.provide_db_conn()
    async def create(self, offer: StudentSellOffer,
                     session: AsyncSession) -> Student:
        return await super().create(session=session, data=offer)

    @BaseModelRepository.provide_db_conn()
    async def is_unpayed(self, worker_id: int,
                         subject_id: int,
                         session: AsyncSession) -> Student:
        return (await session.execute(select(
            self._model.recipient_id,
            self._model.subject_id,
            self._model.is_paid
        ).filter_by(
            recipient_id=worker_id,
            subject_id=subject_id,
            is_paid=False
        ).exists())).scalars()

    @BaseModelRepository.provide_db_conn()
    async def is_selled(self, seller_id,
                        subject_id: int,
                        session: AsyncSession) -> bool:
        return (await session.execute(select(
            self._model.seller_id,
            self._model.subject_id,
            self._model.is_accepted
        ).filter_by(
            seller_id=seller_id,
            subject_id=subject_id,
            is_accepted=True
        ).exists())).scalars()
