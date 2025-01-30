import datetime

from uuid import UUID
import sqlalchemy as sa

from sqlalchemy.orm import (declarative_base,
                            validates,
                            relationship,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)
from sqlalchemy import Column, text, func

from .course import StudentWorkerRelation
from .base import BaseBalanceModel, Base

MAX_STUDENT_NAME_LENGTH = 20
MAX_CITY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 400


class StudentPairRequest(Base):
    __tablename__ = "student_pair_request"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    student_id: Mapped[int] = mapped_column(unique=True)


class Student(BaseBalanceModel):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int | None] = mapped_column(sa.BigInteger(), nullable=True)
    name: Mapped[str] = mapped_column(sa.String(MAX_STUDENT_NAME_LENGTH))
    city: Mapped[str] = mapped_column(sa.String(MAX_CITY_NAME_LENGTH))
    description: Mapped[str] = mapped_column(sa.String(MAX_DESCRIPTION_LENGTH))
    default_rate: Mapped[int]
    registration_date: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())")
    )

    workers: Mapped[list["Worker"]] = relationship(secondary="student_worker_relation",
                                                   back_populates="students",
                                                   lazy="selectin")

    subjects: Mapped[list["Subject"]] = relationship(back_populates="student",
                                                     lazy="selectin")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name=}, {self.city=}, {self.default_rate=})"

    @validates("rate")
    def _validate_rate(self, key: str, rate: float):
        if not (7000 >= rate >= 100):
            raise ValueError("Lesson rate must be >=7000 rub. & =>100 rub.")

        return rate


class StudentSellOffer(Base):
    __tablename__ = "student_sell"

    recipient_id: Mapped[int] = mapped_column(sa.ForeignKey(
        "worker.id", ondelete="SET NULL"
    ))
    seller_id: Mapped[int] = mapped_column(sa.ForeignKey(
        "worker.id", ondelete="SET NULL"
    ))
    subject_id: Mapped[int] = mapped_column(sa.ForeignKey(
        "subject.id", ondelete="SET NULL"
    ))

    cost: Mapped[int]
    is_accepted: Mapped[bool] = mapped_column(default=False)
    is_paid: Mapped[bool] = mapped_column(default=False)
    paid_sum: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())")
    )
    paid_total_at: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime(timezone=True)
    )

    recipient: Mapped["Worker"] = relationship(
        back_populates="income_sell_offers",
        lazy="joined",
        foreign_keys=[recipient_id]
    )

    seller: Mapped["Worker"] = relationship(
        back_populates="outcome_sell_offers",
        lazy="joined",
        foreign_keys=[seller_id]
    )

    subject: Mapped["Subject"] = relationship(
        back_populates="sell_offers",
        lazy="joined",
        foreign_keys=[subject_id]
    )

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @validates("rate")
    def _validate_rate(self, key: str, rate: float):
        if not (7000 >= rate >= 100):
            raise ValueError("Lesson rate must be >=7000 rub. & =>100 rub.")

        return rate
