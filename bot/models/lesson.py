import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates, relationship, mapped_column, Mapped
from sqlalchemy import Column


Base = declarative_base()


class Subject(Base):
    __tablename__ = "subject"

    title: Mapped[str] = mapped_column()


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True)

    worker_id: Mapped[int] = relationship(sa.ForeignKey("worker.id"))
    student_id: Mapped[int] = relationship(sa.ForeignKey("student.id"))

    record_link: Mapped[str] = Column(String(200))
    duration: Mapped[int] = mapped_column()
    date: Mapped[sa.DateTime] = Column(sa.DateTime(timezone=True))
    overriten_rate: Mapped[sa.Null | int] = Column(sa.Integer, nullable=True)
    is_free: Mapped[bool] = Column(sa.Boolean(), default=False)

    @validates("duration")
    def validate_duration(self, key: str, duration: int):
        if not 30 <= duration <= 60*4:
            raise ValueError("Duration must be from 30 min. to 4 hours")

    @validates("is_free")
    def validate_is_free(self, key: str, is_free: bool):
        if is_free and self.overriten_rate:
            raise ValueError("Use `is_free` only without `overriten_rate`")
