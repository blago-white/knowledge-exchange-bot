from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from models.worker import Worker as WorkerModel
from .base import DefaultModelRepository, BaseModelRepository
from .transfer.workers import Worker


class WorkersRepository(DefaultModelRepository):
    _model = WorkerModel

    @property
    def relation_fields_string(self) -> list[str]:
        return [
            "subjects",
            "students",
            "income_sell_offers",
            "outcome_sell_offers"
        ]

    @property
    def relation_fields_mappings(self) -> list[Mapped]:
        return [getattr(self._model, f) for f in self.relation_fields_string]

    @BaseModelRepository.provide_db_conn()
    async def create(self, worker_data: Worker,
                     session: AsyncSession) -> WorkerModel:
        return await super().create(session=session, data=worker_data)

    @BaseModelRepository.provide_db_conn()
    async def add_student(
            self, worker_id: int,
            student: "Student",
            session: AsyncSession
    ) -> WorkerModel:
        worker = await self.get(
            session=session,
            pk=worker_id,
            exclude_related_cols=set(
                self.relation_fields_mappings
            ) ^ {WorkerModel.students}
        )

        worker.students.append(student)

        session.add(worker)

        await session.commit()

    async def _validate_phone(self, phone: str):
        phone = phone.replace(" ", "")

        if not (15 > len(phone) > 10):
            raise Exception("Телефон слишком короткий")

        if not phone.replace("+", "").isdigit():
            raise Exception("Телефон не должен содержать букв и символов")

    async def _validate_meet_link(self, link: str):
        link = link.replace(" ", "")

        if "https://" not in link:
            raise Exception("Ссылка нерабочая [нет 'https://']")

        if len(link) < 10:
            raise Exception("Ссылка слишком короткая")
