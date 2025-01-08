import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sqlalchemy import Column

from .course import StudentWorkerRelation
from .base import Base

MAX_WORKER_FIRST_NAME_LENGTH = 20
MAX_WORKER_LAST_NAME_LENGTH = 20
MAX_DESCRIPTION_LENGTH = 400
CARD_NUMBER_LENGTH = 16
MAX_MEET_LINK_LENGTH = 100


class Worker(Base):
    __tablename__ = "worker"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    phone_number: Mapped[str | None] = mapped_column(nullable=True)
    firstname: Mapped[str] = mapped_column(
        sa.String(MAX_WORKER_FIRST_NAME_LENGTH))
    lastname: Mapped[str] = mapped_column(
        sa.String(MAX_WORKER_LAST_NAME_LENGTH))
    description: Mapped[str] = mapped_column(sa.String(MAX_DESCRIPTION_LENGTH))
    bank_card_number: Mapped[str | None] = mapped_column(
        sa.String(CARD_NUMBER_LENGTH), nullable=True
    )
    meet_link: Mapped[str] = mapped_column(sa.String(MAX_MEET_LINK_LENGTH))
    balance: Mapped[float] = mapped_column(default=0.0)

    lesson: Mapped[list["Lesson"]] = relationship(back_populates="worker",
                                                  lazy="selectin")

    subjects: Mapped[list["Subject"]] = relationship(back_populates="worker",
                                                     lazy="selectin")

    students: Mapped[list["Student"]] = relationship(secondary="student_worker_relation",
                                                     back_populates="workers",
                                                     lazy="selectin")
    messages: Mapped[list["Message"]] = relationship(back_populates="worker",
                                                     lazy="joined")
    income_sell_offers: Mapped[list["StudentSellOffer"]] = relationship(
        back_populates="recipient",
        primaryjoin="Worker.id==StudentSellOffer.recipient_id"
    )
    outcome_sell_offers: Mapped[list["StudentSellOffer"]] = relationship(
        back_populates="seller",
        primaryjoin="Worker.id==StudentSellOffer.seller_id"
    )

    def __repr__(self):
        try:
            return f"Worker({self.id=}, {self.firstname=}, {self.phone_number=})"
        except sa.orm.exc.DetachedInstanceError:
            return f"Worker(self.id=None, {self.firstname=}, {self.phone_number=})"

    @validates("balance")  # TODO: Add parent with this method
    def _validate_balance(self, key: str, balance: float):
        if balance < 0:
            raise ValueError("Balance cannot be < 0")

        return balance

    @validates("phone_number")
    def _validate_phone(self, key: str, number: str):
        if not 12 <= len(number) <= 15:
            raise ValueError(f"Not correct phone number len [{len(number)}]")

        if number[0] != "+":
            raise ValueError(f"Use plus as first symbol")

        if not number[1:].isdigit():
            raise ValueError(f"Phone number can contain only digits")

        return number

    @validates("bank_card_number")
    def _validate_card(self, key: str, number: str):
        if number and not number.isdigit():
            raise ValueError(f"Card number can contain only digits")

        return number
