from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.worker import Worker as WorkerModel
from .base import DefaultModelRepository, BaseModelRepository
from .transfer.workers import Worker


class WorkersRepository(DefaultModelRepository):
    _model = WorkerModel

    @BaseModelRepository._provide_db_conn()
    async def create(self, worker_data: Worker,
                     session: AsyncSession) -> WorkerModel:
        return await super().create(session=session, data=worker_data)
