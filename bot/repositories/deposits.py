import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models.deposits import Deposit

from .base import BaseModelRepository, DefaultModelRepository, Model


class DepositsModelRepository(DefaultModelRepository):
    _telegram_id: int = None
    _model = Deposit

    @BaseModelRepository.provide_db_conn()
    async def create(self, deposit: Deposit,
                     session: AsyncSession = None) -> Deposit:
        await self._drop_all_uncoplete(telegram_id=deposit.user_telegram_id, session=session)

        return await super().create(data=deposit, session=session)

    @BaseModelRepository.provide_db_conn()
    async def get_by_telegram_id(self, telegram_id: int,
                                 session: AsyncSession = None) -> Deposit:
        return (await session.execute(sa.select(self._model).filter(
            Deposit.user_telegram_id == telegram_id,
            Deposit.success == None
        ))).one_or_none()[0]

    @BaseModelRepository.provide_db_conn()
    async def set_success(self, telegram_id: int, session: AsyncSession) -> Deposit:
        payment = await self.get_by_telegram_id(telegram_id=telegram_id,
                                                session=session)

        payment.success = True

        await session.commit()

        return payment

    @BaseModelRepository.provide_db_conn()
    async def set_paid(self, telegram_id: int, session: AsyncSession):
        payment = await self.get_by_telegram_id(telegram_id=telegram_id)

        print(payment, type(payment))

        payment.paid = True

        session.add(payment)

        await session.commit()

        await session.refresh(payment)

        return payment

    @BaseModelRepository.provide_db_conn()
    async def _drop_all_uncoplete(self, telegram_id: int,
                                  session: AsyncSession):
        try:
            exists = await self.get_by_telegram_id(telegram_id=telegram_id)

            exists.success = False

            session.add(exists)

            await session.commit()
        except Exception as e:
            print(f"ERROR DROP UNCOMPLETE {e}")
            pass
