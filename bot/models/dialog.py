import datetime
import pytz

from enum import Enum
import sqlalchemy as sa

from sqlalchemy.orm import (declarative_base,
                            validates,
                            relationship,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)
from sqlalchemy import Column, text

from .base import Base


class SenderType(Enum):
    WORKER = "w"
    STUDENT = "s"


class Message(Base):
    __tablename__ = "dialog_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        sa.ForeignKey("subject.id", ondelete="SET NULL")
    )
    sended_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())")
    )
    sender: Mapped[SenderType]
    text: Mapped[str] = mapped_column(sa.String(4096))

    subject: Mapped["Subject"] = relationship(
        back_populates="messages",
        lazy="joined"
    )

    @property
    def display_sended_at(self) -> str:
        lesson_datetime_format = "%d.%m %H:%M"
        lesson_date_msc = self.sended_at.astimezone(pytz.timezone("Europe/Moscow"))

        try:
            return lesson_date_msc.strftime(lesson_datetime_format)
        except:
            return
