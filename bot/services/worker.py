import datetime

from models.lesson import Subject, Lesson
from models.worker import Worker
from models.student import StudentSellOffer
from repositories.base import BaseModelRepository
from repositories.lessons import LessonsModelRepository
from repositories.workers import WorkersRepository
from repositories.subjects import SubjectsModelRepository
from repositories.dialog import DialogRepository
from repositories.students import StudentsSellOffersModelRepository
from .base import BaseModelService


class WorkersService(BaseModelService):
    workers_repository = WorkersRepository()
    lessons_repository = LessonsModelRepository()
    sell_offers_repository = StudentsSellOffersModelRepository()
    subjects_repository = SubjectsModelRepository()
    dialogs_repository = DialogRepository()

    _worker_id: int | None

    def __init__(self, **kwargs):
        self.__dict__ |= {f"_{name}": getattr(self, name)
                          for name in dir(self)
                          if "repository" in name and name != "repository"}

        for kw_name in kwargs:
            self.__dict__.update(
                {f"_{kw_name}": kwargs.get(kw_name)}
            )

    @property
    def repository(self) -> WorkersRepository:
        return self._workers_repository

    async def get_or_create(self, username: str, tag: str) -> tuple[bool, Worker]:
        try:
            result = await self.workers_repository.get(pk=self._worker_id)

            if not result:
                raise ValueError

            return False, result
        except Exception as e:
            await self.workers_repository.create(worker_data=Worker(
                id=self._worker_id,
                firstname=username,
                lastname=tag,
            ))

            return True, (await self.get_or_create(username=username, tag=tag))[-1]

    async def get_selled_students_count(self) -> int:
        worker: Worker = await self._workers_repository.get(
            pk=self._worker_id,
            exclude_related_cols=set(
                self._workers_repository.relation_fields_mappings
            ) ^ {Worker.outcome_sell_offers}
        )

        return len(worker.outcome_sell_offers)

    @BaseModelRepository.provide_db_conn()
    async def get_week_profit(self, session) -> int:
        worker: Worker = await self._workers_repository.get(
            session=session,
            pk=self._worker_id,
        )

        if not worker:
            print(await self.workers_repository.get_all())
            raise ValueError("Worker not exists!")

        profit_for_week = await self._lessons_repository.get_week_lessons_pay(
            *(s.id for s in worker.subjects)
        )

        return profit_for_week

    async def sell_student(
            self, buyer_worker_id: int,
            subject_id: int,
            cost: int):
        await self._can_sell_subject(subject_id=subject_id)

        await self._sell_offers_repository.create(offer=StudentSellOffer(
            recipient_id=buyer_worker_id,
            subject_id=subject_id,
            seller_id=self._worker_id,
            cost=cost
        ))

    async def get_selled_student_lessons(
            self, subject_id: int
    ) -> list["Lesson"]:
        await self._check_selled_subject(subject_id=subject_id)

        sell_offer = (
            await self.sell_offers_repository.get(subject_id=subject_id))

        return await self.lessons_repository.get_lessons_for_period(
            subject_id=subject_id,
            start=sell_offer.created_at,
            end=sell_offer.paid_total_at
        )

    async def get_selled_student_status(
            self, subject_id: int
    ) -> "StudentSellOffer":
        await self._check_selled_subject(subject_id=subject_id)

        return await self.sell_offers_repository.get(subject_id=subject_id)

    async def get_active_subjects(self) -> list["Subject"]:
        return self.workers_repository.get(
            self._worker_id,
            exclude_related_cols=set(
                self._workers_repository.relation_fields_mappings
            ) ^ {Worker.subjects}
        ).subjects

    async def get_dialog(self, subject_id: int):
        if (
                await self.subjects_repository.get(pk=subject_id)
        ).worker_id != self._worker_id:
            if (await self.sell_offers_repository.get(
                subject_id=subject_id
            )).is_paid:
                raise Exception("Cannot view dialog, student is paid!")
            else:
                raise Exception("Cannot view dialog, you are not seller of student!")

        return self.dialogs_repository.get_all_for_subject(
            subject_id=subject_id
        )

    async def get_total_profit(self):
        worker_subjects = (await self.workers_repository.get(
            pk=self._worker_id,
            exclude_related_cols=set(
                self._workers_repository.relation_fields_mappings
            ) ^ {Worker.subjects}
        )).subjects

        profit_for_lessons = await self.lessons_repository.get_completed_lessons_payment_amount(
            subjects=worker_subjects
        )

        selled_amount = await self.sell_offers_repository.get_total_revenue(worker_id=self._worker_id)

        print(f"{profit_for_lessons=} {selled_amount=}")

        return profit_for_lessons + selled_amount

    async def get_selled_count(self) -> int:
        return await self.sell_offers_repository.get_selled_count(worker_id=self._worker_id)

    async def _check_selled_subject(self, subject_id: int):
        if not self.sell_offers_repository.is_selled(
                seller_id=self._worker_id, subject_id=subject_id
        ):
            raise Exception("Subject is not selled!")

    async def _can_sell_subject(self, subject_id: int):
        if not await self._subjects_repository.worker_has_subject(
                worker_id=self._worker_id,
                subject_id=subject_id
        ):
            raise Exception("Seller dont have subject!")

        if await self.sell_offers_repository.is_unpayed(
                worker_id=self._worker_id, subject_id=subject_id
        ):
            raise Exception("Student payments is not complete!")
