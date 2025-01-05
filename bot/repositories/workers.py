from .transfer.workers import Worker

from ..models.worker import Worker as WorkerModel

from .base import BaseModelRepository


class WorkersRepository(BaseModelRepository):
    _model = WorkerModel

    async def create(self, worker_data: Worker) -> Worker:
        ...

    async def update(self, worker_data: Worker) -> Worker:
        ...
