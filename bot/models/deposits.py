import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Deposit(Base):
    __tablename__ = "deposit"

    amount: Mapped[int] = mapped_column()
    user_telegram_id: Mapped[int] = mapped_column(sa.BigInteger)

    paid: Mapped[bool] = mapped_column(default=False)
    success: Mapped[bool] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.text("TIMEZONE('utc', now())")
    )

    __table_args__ = (
        sa.CheckConstraint(amount >= 100, name='check_amount_gte_100'),
        sa.CheckConstraint(amount <= 30000, name='check_amount_lte_30000'),
    )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.amount=}, {self.user_telegram_id=})"
