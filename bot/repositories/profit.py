from sqlalchemy.ext.asyncio import AsyncSession

from models.profit import AppProfitDelta
from .base import BaseModelRepository


class AppProfitRepository(BaseModelRepository):
    _model = AppProfitDelta

    @BaseModelRepository.provide_db_conn(make_commit=True)
    async def add(self, amount: float, session: AsyncSession):
        delta = self._model(delta=amount)

        session.add(delta)
