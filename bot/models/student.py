import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy import Column

MAX_STUDENT_NAME_LENGTH = 20
MAX_CITY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 400

Base = declarative_base()


class Student(Base):
    __tablename__ = "student"

    id = Column(sa.Integer, primary_key=True)
    balance = Column(sa.Float)
    name = Column(sa.String(MAX_STUDENT_NAME_LENGTH))
    city = Column(sa.String(MAX_CITY_NAME_LENGTH))
    description = Column(sa.String(MAX_DESCRIPTION_LENGTH))
    subject = Column(sa.String, sa.ForeignKey("subject.title"))
    rate = Column(sa.Integer())
    registration_date = Column(sa.DateTime(timezone=True))

    @validates(balance)
    def validate_balance(self, key: str, balance: float):
        if balance < 0:
            raise ValueError("Balance cannot be < 0")

    @validates("rate")
    def validate_rate(self, key: str, rate: float):
        if not (7000 >= rate >= 100):
            raise ValueError("Lesson rate must be >=7000 rub. & =>100 rub.")
