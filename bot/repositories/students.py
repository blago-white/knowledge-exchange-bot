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
    async def get_by_telegram(self, telegram_id: int, session: AsyncSession):
        return (await session.execute(select(self._model).filter_by(
            telegram_id=telegram_id
        ))).unique().scalars().one_or_none()

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
    async def get_by_subject_id(self, subject_id: int,
                                session: AsyncSession,
                                seller_id: int = None,
                                ) -> StudentSellOffer:
        query_kwargs = dict(subject_id=subject_id) | (dict(seller_id=seller_id) if seller_id else {})

        print(query_kwargs)

        return (await session.execute(select(self._model).filter_by(
            **query_kwargs,
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
    async def is_unpayed(self, subject_id: int,
                         session: AsyncSession,
                         seller_id: int = None,
                         worker_id: int = None) -> Student:
        worker_filter_params: dict

        if seller_id:
            worker_filter_params = dict(seller_id=seller_id)
        elif worker_id:
            worker_filter_params = dict(recipient_id=worker_id)
        else:
            raise ValueError("Required `seller_id` or `worker_id`")

        query = select(select(
            self._model
        ).filter_by(
            **worker_filter_params,
            subject_id=subject_id,
            is_paid=False
        ).exists())

        return await session.scalar(query)

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

    @BaseModelRepository.provide_db_conn()
    async def get_selled(self, seller_id: int,
                         session: AsyncSession):
        return list((await session.execute(select(
            self._model
        ).filter_by(
            seller_id=seller_id,
        ).order_by(
            self._model.is_accepted.asc(),
            self._model.is_paid.asc(),
            self._model.cost.desc()
        ))).scalars())
