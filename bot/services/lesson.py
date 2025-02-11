import datetime
from pytz import UTC
from sqlalchemy.ext.asyncio import AsyncSession

from models.lesson import Lesson, Subject, LessonStatus
from repositories.lessons import LessonsModelRepository
from repositories.subjects import SubjectsModelRepository
from repositories.workers import WorkersRepository
from repositories.students import StudentsSellOffersModelRepository
from repositories.base import BaseModelRepository

from .transfer.subjects import SubjectsInitializingData
from .transfer.lessons import LessonCompleteResult
from .exceptions import lessons as lessons_exceptions
from .base import BaseModelService


class LessonsService(BaseModelService):
    _repository = LessonsModelRepository()
    workers_repository = WorkersRepository()
    sell_offers_repository = StudentsSellOffersModelRepository()

    _lesson_id: int | None

    def __init__(
            self, *args,
            lesson_id: int = None,
            lessons_repository: LessonsModelRepository = None,
            **kwargs):
        self._lesson_id = lesson_id
        self._repository = lessons_repository or self._repository

        super().__init__(*args, **kwargs)

    @property
    def repository(self) -> LessonsModelRepository:
        return self._repository

    @property
    def lesson_id(self):
        return self._lesson_id

    @lesson_id.setter
    def lesson_id(self, new_lesson_id: int):
        self._lesson_id = new_lesson_id

    async def retrieve(self, worker_id: int):
        lesson: Lesson = await self._repository.get(pk=self._lesson_id)

        if not lesson.subject.worker_id == worker_id:
            raise ValueError("Cannot retrieve this lesson!")

        return lesson

    @BaseModelRepository.provide_db_conn()
    async def complete_lesson(self, worker_id: int, session: AsyncSession):
        lesson: Lesson = await self._repository.get(pk=self._lesson_id,
                                                    session=session)

        if lesson.subject.worker_id != worker_id:
            raise PermissionError("You not teacher!")

        lesson_rate = lesson.overriten_rate or lesson.subject.rate
        lesson_price = lesson_rate * (lesson.duration / 60) * int(not lesson.is_free)

        print(f"LESSON PRICE: {lesson_price} = {lesson_rate} * {lesson.duration} / 60")

        await self._validate_complition(lesson=lesson,
                                        student=lesson.subject.student,
                                        lesson_price=lesson_price)

        offer = await self.sell_offers_repository.get_by_subject_id(
            subject_id=lesson.subject_id,
            session=session
        )

        complete_result = LessonCompleteResult(
            worker_id=lesson.subject.worker_id,
        )

        if offer:
            complete_result.seller_id = offer.seller_id

            if not offer.is_paid:
                complete_result.for_paid = True

                if offer.paid_sum + lesson_price >= offer.cost:
                    lesson.subject.worker.balance += offer.paid_sum + lesson_price - offer.cost

                    offer.is_paid = True
                    offer.paid_total_at = datetime.datetime.now()

                    complete_result.paid_total_now = True

                offer.seller.balance += lesson_price
                offer.paid_sum += lesson_price
                lesson.for_offer_payment = True

            else:
                lesson.subject.worker.balance += lesson_price
        else:
            lesson.subject.worker.balance += lesson_price

        lesson.is_completed = True
        lesson.status = LessonStatus.SUCCESS
        lesson.subject.student.balance -= lesson_price

        if lesson.subject.student.balance <= lesson_price:
            complete_result.low_balance_student = True

        complete_result.subject = lesson.subject
        complete_result.offer = offer

        try:
            session.add(lesson)
        except:
            await session.rollback()
        else:
            await session.commit()
            await session.refresh(lesson)

        return complete_result

    async def update(self, worker_id: int, **params):
        lesson: Lesson = await self._repository.get(
            pk=self._lesson_id,
        )

        if not lesson.subject.worker_id == worker_id:
            raise ValueError("Cannot update this lesson!")

        return await self._repository.update(pk=self._lesson_id,
                                             **params)

    async def drop(self, worker_id: int):
        await self.retrieve(worker_id=worker_id)

        await self._repository.update(
            pk=self._lesson_id,
            status=LessonStatus.CANCELED
        )

        return True

    async def _validate_complition(self, lesson: Lesson,
                                   student: "Student",
                                   lesson_price: int):
        if lesson.date > (datetime.datetime.now(tz=UTC) + datetime.timedelta(minutes=lesson.duration)):
            raise lessons_exceptions.CompliteLessonDateUncorrect()

        if lesson.status == LessonStatus.SUCCESS:
            raise ValueError("Already successed!")

        if student.balance < lesson_price:
            raise lessons_exceptions.StudentBalanceEmpty()


class SubjectsService(BaseModelService):
    _repository = SubjectsModelRepository()

    _subject_id: int = None
    _subject_title: str | None

    def __init__(
            self, *args,
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

    async def invert_active_status(self, worker_id: int):
        subject = await self._repository.get(pk=self._subject_id)

        if subject.worker_id != worker_id:
            raise PermissionError()

        return await self._repository.update(
            pk=self._subject_id, is_active=not subject.is_active
        )

    async def initialize(self, data: SubjectsInitializingData) -> int:
        return (await self._repository.create(
            subject_data=Subject(**data.__dict__)
        )).id

    async def get_lessons(self, worker_id: int,
                          for_payment: bool = False):
        if await self.repository.worker_has_subject(
                subject_id=self._subject_id, worker_id=worker_id
        ):
            lesson: Lesson
            lessons: list[Lesson] = sorted(list((await self.repository.get(
                pk=self._subject_id,
                exclude_related_cols=[
                    Subject.sell_offers,
                    Subject.messages,
                    Subject.student,
                ]
            )).lessons), key=lambda lesson: lesson.date)

            # if for_payment:
            #     lessons = [l for l in lessons if l.for_offer_payment]

            return lessons

        raise ValueError("You is not owner!")
