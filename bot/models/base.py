from sqlalchemy.orm import (declarative_base,
                            validates,
                            relationship,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)


class BaseBalanceModel(Base):
    __abstract__ = True

    balance: Mapped[float] = mapped_column(default=0.0)

    @validates("balance")
    def _validate_balance(self, key: str, balance: float):
        if balance < 0:
            raise ValueError("Balance cannot be < 0")

        return balance
