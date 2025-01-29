import datetime
import pytz
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates, relationship, mapped_column, Mapped
from sqlalchemy import Column

from .base import Base


class WeekDay(Enum):
    MONDAY = "WO"
    TUESDAY = "TU"
    WEDNESDAY = "WE"
    THURSDAY = "TH"
    FRIDEY = "FR"
    SATURDAY = "SA"
    SUNDAY = "SU"


class LessonStatus(Enum):
    SUCCESS = "S"
    CANCELED = "C"
    SCHEDULED = "H"


class Subject(Base):
    __tablename__ = "subject"

    worker_id: Mapped[int] = mapped_column(
        sa.ForeignKey("worker.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    student_id: Mapped[int] = mapped_column(
        sa.ForeignKey("student.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    sell_offers: Mapped[list["StudentSellOffer"]] = relationship(
        back_populates="subject",
        lazy="selectin"
    )
    title: Mapped[str] = mapped_column(sa.String(100))
    rate: Mapped[int]
    description: Mapped[str | None] = mapped_column(
        sa.String(500),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    worker: Mapped["Worker"] = relationship(
        back_populates="subjects",
        lazy="joined"
    )
    student: Mapped["Student"] = relationship(
        back_populates="subjects",
        lazy="selectin"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="subject",
        lazy="selectin"
    )

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="subject",
        lazy="selectin"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title=})"

    @validates("rate")
    def _validate_rate(self, key: str, rate: float):
        if not (7000 >= rate >= 100):
            raise ValueError("Lesson rate must be >=7000 rub. & =>100 rub.")

        return rate


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)

    subject_id: Mapped[int] = mapped_column(
        sa.ForeignKey("subject.id", ondelete="SET NULL")
    )

    record_link: Mapped[str | None] = mapped_column(sa.String(200))

    duration: Mapped[int]
    date: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))

    overriten_rate: Mapped[int | None]
    is_free: Mapped[bool] = mapped_column(default=False)
    is_completed: Mapped[bool] = mapped_column(default=False)
    status: Mapped[LessonStatus] = mapped_column(default=LessonStatus.SCHEDULED)

    subject: Mapped[Subject] = relationship(
        back_populates="lessons",
        lazy="joined"
    )

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.subject_id=}, "
                f"{self.date=}, "
                f"{self.duration=}min"
                f")")

    @property
    def display_duration(self) -> str:
        try:
            return f"{self.duration}мин."
        except:
            return

    @property
    def display_date(self) -> str:
        lesson_datetime_format = "%m.%d %H:%M"
        lesson_date_msc = self.date.astimezone(pytz.timezone("Europe/Moscow"))

        try:
            return lesson_date_msc.strftime(lesson_datetime_format)
        except:
            return

    @validates("duration")
    def _validate_duration(self, key: str, duration: int):
        if not 30 <= duration <= 60*4:
            raise ValueError("Duration must be from 30 min. to 4 hours")

        return duration

    @validates("is_free")
    def _validate_is_free(self, key: str, is_free: bool):
        if is_free and self.overriten_rate:
            raise ValueError("Use `is_free` only without `overriten_rate`")

        return is_free
