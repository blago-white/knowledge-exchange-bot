import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column


MAX_WORKER_FIRST_NAME_LENGTH = 20
MAX_WORKER_LAST_NAME_LENGTH = 20
MAX_DESCRIPTION_LENGTH = 400
CARD_NUMBER_LENGTH = 16
MAX_MEET_LINK_LENGTH = 100

Base = declarative_base()


class Worker(Base):
    __tablename__ = "worker"

    id = Column(sa.Integer, primary_key=True)
    phone_number = Column(sa.String)
    firstname = Column(sa.String(MAX_WORKER_FIRST_NAME_LENGTH),)
    lastname = Column(sa.String(MAX_WORKER_LAST_NAME_LENGTH))
    description = Column(sa.String(MAX_DESCRIPTION_LENGTH))
    bank_card_number = Column(sa.String(CARD_NUMBER_LENGTH),
                              nullable=True)
    meet_link = Column(sa.String(MAX_MEET_LINK_LENGTH))
    subjects: Mapped[list["Subject"]] = relationship()

    @validates("phone_number")
    def validate_phone(self, key: str, number: str):
        if not 12 <= len(number) <= 15:
            raise ValueError(f"Not correct phone number len [{len(number)}]")

        if number[0] != "+":
            raise ValueError(f"Use plus as first symbol")

        if not number[1:].isdigit():
            raise ValueError(f"Phone number can contain only digits")

    @validates("bank_card_number")
    def validate_card(self, key: str, number: str):
        if number and not number.isdigit():
            raise ValueError(f"Card number can contain only digits")
