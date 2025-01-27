import datetime
import typing

from sqlalchemy import select, func, Integer, not_
from sqlalchemy.ext.asyncio import AsyncSession

from models.lesson import Lesson, Subject

from .base import DefaultModelRepository, BaseModelRepository


class LessonsModelRepository(DefaultModelRepository):
    _model = Lesson

    @BaseModelRepository.provide_db_conn()
    async def create(
            self, lesson_data: Lesson,
            session: AsyncSession) -> Lesson:
        return await super().create(session=session, data=lesson_data)

    @BaseModelRepository.provide_db_conn()
    async def bulk_create_lessons(self, session: AsyncSession,
                                  lesson_data: dict,
                                  copies: int):
        lesson_date = lesson_data.pop("date")

        lesson_dates = [
            lesson_date + (datetime.timedelta(days=7 * i))
            for i in range(copies)
        ]

        session.add_all(
            [self._model(**lesson_data | {"date": date}) for date in
             lesson_dates]
        )

    @BaseModelRepository.provide_db_conn()
    async def get_completed_lessons_payment_amount(
            self, subjects: typing.Collection[Subject],
            session: AsyncSession
    ) -> list[Lesson]:
        return (await session.execute(select(
            func.sum(
                (self._model.duration/60)*Subject.rate
            )
        ).filter(
            self._model.is_completed is True,
            Subject.id.in_([subject.id for subject in subjects])
        ))).scalar() or 0

    @BaseModelRepository.provide_db_conn()
    async def get_course_lessons(self, session: AsyncSession,
                                 subject_id: int):
        return (await session.execute(select(self._model).filter_by(
            subject_id=subject_id
        ))).scalars()

    @BaseModelRepository.provide_db_conn()
    async def get_lessons_for_period(self, subject_id: int,
                                     start: datetime.datetime,
                                     end: datetime.datetime):
        return (await session.execute(select(self._model).filter_by(
            subject_id=subject_id,
        ).where(
            Lesson.date >= start,
            Lesson.date <= end
        ))).scalars()

    @BaseModelRepository.provide_db_conn()
    async def get_week_lessons_pay(
            self, *subjects_ids: tuple[int], session: AsyncSession
    ):
        start_week, end_week = self._get_week_borders()

        pay_sum = (await session.execute(select(
            func.sum(
                self._model.overriten_rate *
                self._model.duration *
                not_(self._model.is_free).cast(Integer) / 60
            ).cast(Integer).label("overriten_profit"),
            func.sum(
                Subject.rate *
                self._model.duration *
                not_(self._model.is_free).cast(Integer) / 60
            ).cast(Integer).label("subject_profit"),
        ).join(Subject).where(
            self._model.date >= start_week,
            self._model.date < end_week,
            self._model.subject_id.in_(subjects_ids),

        ).group_by(self._model.id)))

        return sum([(pay[0] or pay[1]) for pay in pay_sum])

    @staticmethod
    def _get_week_borders() -> tuple[int, int]:
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())

        return start, (start + datetime.timedelta(days=7))
