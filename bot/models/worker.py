import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sqlalchemy import Column

from .base import Base


MAX_WORKER_FIRST_NAME_LENGTH = 20
MAX_WORKER_LAST_NAME_LENGTH = 20
MAX_DESCRIPTION_LENGTH = 400
CARD_NUMBER_LENGTH = 16
MAX_MEET_LINK_LENGTH = 100


class Worker(Base):
    __tablename__ = "worker"

    phone_number: Mapped[str | None] = mapped_column(nullable=True)
    firstname: Mapped[str] = mapped_column(sa.String(MAX_WORKER_FIRST_NAME_LENGTH))
    lastname: Mapped[str] = mapped_column(sa.String(MAX_WORKER_LAST_NAME_LENGTH))
    description: Mapped[str] = mapped_column(sa.String(MAX_DESCRIPTION_LENGTH))
    bank_card_number: Mapped[str | None] = mapped_column(
        sa.String(CARD_NUMBER_LENGTH), nullable=True
    )
    meet_link: Mapped[str] = mapped_column(sa.String(MAX_MEET_LINK_LENGTH))

    lesson: Mapped[list["Lesson"]] = relationship(back_populates="worker",
                                                  lazy="selectin")

    subjects: Mapped[list["Subject"]] = relationship(back_populates="worker",
                                                     lazy="selectin")

    def __repr__(self):
        try:
            return f"Worker({self.id=}, {self.firstname=}, {self.phone_number=})"
        except sa.orm.exc.DetachedInstanceError:
            return f"Worker(self.id=None, {self.firstname=}, {self.phone_number=})"

    @validates("phone_number")
    def validate_phone(self, key: str, number: str):
        if not 12 <= len(number) <= 15:
            raise ValueError(f"Not correct phone number len [{len(number)}]")

        if number[0] != "+":
            raise ValueError(f"Use plus as first symbol")

        if not number[1:].isdigit():
            raise ValueError(f"Phone number can contain only digits")

        return number

    @validates("bank_card_number")
    def validate_card(self, key: str, number: str):
        if number and not number.isdigit():
            raise ValueError(f"Card number can contain only digits")

        return number
