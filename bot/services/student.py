import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.student import Student, StudentPairRequest
from models.lesson import Lesson
from repositories.students import StudentsModelRepository
from repositories.base import BaseModelRepository

from .transfer.student import StudentInitializingData
from .base import BaseModelService


class StudentsService(BaseModelService):
    _repository = StudentsModelRepository()
    _student_ref_tokens_model = StudentPairRequest
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

    @BaseModelRepository.provide_db_conn()
    async def ref_token_exists(self, ref_token: str = None, session: AsyncSession = None):
        try:
            return (await session.execute(
                select(self._student_ref_tokens_model).filter_by(
                    student_id=self._student_id
                )
            )).unique().scalars().one_or_none()
        except:
            try:
                return (await session.execute(
                    select(self._student_ref_tokens_model).filter_by(
                        id=ref_token
                    )
                )).unique().scalars().one_or_none()
            except:
                return

    @BaseModelRepository.provide_db_conn()
    async def generate_ref_token(self, session: AsyncSession):
        if await self.ref_token_exists():
            raise ValueError("Ref Token exists")

        new_request = StudentPairRequest(student_id=self._student_id)

        session.add(new_request)

        await session.commit()

        await session.refresh(new_request)

        return new_request

    async def initialize(self, student_data: StudentInitializingData) -> int:
        result = await self._repository.create(student_data=Student(
            **student_data.__dict__
        ))

        return result.id

    async def connect_student_telegram(self):
        if not (self._telegram_id and self._student_id):
            raise ValueError("Cannot connect tg id, `_telegram_id` and "
                             "`_student_id` must be setted")

        if (await self._repository.get(pk=self._student_id)).telegram_id:
            raise ValueError("Telegram Id exists")

        await self._repository.update(
            pk=self._student_id,
            telegram_id=self._telegram_id
        )

        return True

    @BaseModelRepository.provide_db_conn()
    async def get_nearest_lesson(self, session: AsyncSession):
        subjects = (await self._repository.get_by_telegram(
            telegram_id=self._student_id,
            session=session
        )).subjects

        try:
            return (await session.execute(select(Lesson).filter(Lesson.subject_id.in_(
                [s.id for s in subjects]
            )).order_by(Lesson.date.desc()).limit(1))).one_or_none()[0]
        except:
            return None
