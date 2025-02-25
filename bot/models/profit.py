import datetime

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class AppProfitDelta(Base):
    __tablename__ = "app_profit"

    delta: Mapped[float] = mapped_column(default=0)
    date: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.text("TIMEZONE('utc', now())")
    )
