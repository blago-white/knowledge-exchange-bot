import datetime
import sqlalchemy as sa

from sqlalchemy.orm import (declarative_base,
                            validates,
                            relationship,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)
from sqlalchemy import Column, text

from .base import Base

MAX_STUDENT_NAME_LENGTH = 20
MAX_CITY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 400


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[float]
    name: Mapped[str] = mapped_column(sa.String(MAX_STUDENT_NAME_LENGTH))
    city: Mapped[str] = mapped_column(sa.String(MAX_CITY_NAME_LENGTH))
    description: Mapped[str] = mapped_column(sa.String(MAX_DESCRIPTION_LENGTH))
    subject_id: Mapped[int] = mapped_column(
        sa.ForeignKey("subject.id", ondelete="SET NULL")
    )
    rate: Mapped[int]
    registration_date: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())")
    )

    lessons: Mapped[list["Lesson"]] = relationship(back_populates="student")
    subject: Mapped["Subject"] = relationship(back_populates="student")

    @validates("balance")
    def validate_balance(self, key: str, balance: float):
        if balance < 0:
            raise ValueError("Balance cannot be < 0")

        return balance

    @validates("rate")
    def validate_rate(self, key: str, rate: float):
        if not (7000 >= rate >= 100):
            raise ValueError("Lesson rate must be >=7000 rub. & =>100 rub.")

        return rate
