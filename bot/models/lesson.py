import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates, relationship, mapped_column, Mapped
from sqlalchemy import Column

from .base import Base


class Subject(Base):
    __tablename__ = "subject"

    worker_id: Mapped[int] = mapped_column(
        sa.ForeignKey("worker.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    worker: Mapped["Worker"] = relationship(back_populates="subjects")
    student: Mapped["Student"] = relationship(back_populates="subject")
    title: Mapped[str] = mapped_column(sa.String(100))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title=})"


class Lesson(Base):
    __tablename__ = "lesson"

    worker_id: Mapped[int] = mapped_column(
        sa.ForeignKey("worker.id", ondelete="SET NULL"),
    )
    student_id: Mapped[int] = mapped_column(
        sa.ForeignKey("student.id", ondelete="SET NULL"),
    )

    record_link: Mapped[str] = mapped_column(sa.String(200))
    duration: Mapped[int] = mapped_column()
    date: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    overriten_rate: Mapped[int | None] = mapped_column()
    is_free: Mapped[bool] = mapped_column(default=False)

    worker: Mapped["Worker"] = relationship(back_populates="lesson")
    student: Mapped["Student"] = relationship(back_populates="lessons")

    @validates("duration")
    def validate_duration(self, key: str, duration: int):
        if not 30 <= duration <= 60*4:
            raise ValueError("Duration must be from 30 min. to 4 hours")

    @validates("is_free")
    def validate_is_free(self, key: str, is_free: bool):
        if is_free and self.overriten_rate:
            raise ValueError("Use `is_free` only without `overriten_rate`")
