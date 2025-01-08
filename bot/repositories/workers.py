from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from models.worker import Worker as WorkerModel
from .base import DefaultModelRepository, BaseModelRepository
from .transfer.workers import Worker


class WorkersRepository(DefaultModelRepository):
    _model = WorkerModel

    @property
    def _relation_fields_string(self) -> list[str]:
        return [
            "lesson",
            "subjects",
            "students",
            "messages",
            "income_sell_offers",
            "outcome_sell_offers"
        ]

    @property
    def _relation_fields_mappings(self) -> list[Mapped]:
        return [getattr(self._model, f) for f in self._relation_fields_string]

    @BaseModelRepository._provide_db_conn()
    async def create(self, worker_data: Worker,
                     session: AsyncSession) -> WorkerModel:
        return await super().create(session=session, data=worker_data)

    @BaseModelRepository._provide_db_conn()
    async def add_student(
            self, worker_id: int,
            student: "Student",
            session: AsyncSession
    ) -> WorkerModel:
        worker = await self.get(
            session=session,
            pk=worker_id,
            exclude_related_cols=set(
                self._relation_fields_mappings
            ) ^ {WorkerModel.students}
        )

        worker.students.append(student)

        session.add(worker)

        await session.commit()
