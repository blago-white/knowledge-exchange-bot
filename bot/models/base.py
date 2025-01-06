from sqlalchemy.orm import (declarative_base,
                            validates,
                            relationship,
                            Mapped,
                            mapped_column,
                            DeclarativeBase)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
