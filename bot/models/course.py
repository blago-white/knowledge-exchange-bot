import datetime

import sqlalchemy as sa
from sqlalchemy import text, Column
from sqlalchemy.orm import (Mapped,
                            mapped_column)

from .base import Base

StudentWorkerRelation = sa.Table(
    'student_worker_relation',
    Base.metadata,
    Column('student_id',
           sa.Integer,
           sa.ForeignKey("student.id", ondelete="CASCADE"),
           primary_key=True
           ),
    Column('worker_id',
           sa.Integer,
           sa.ForeignKey("worker.id", ondelete="CASCADE"),
           primary_key=True
           ),
    Column('date_started',
           sa.DateTime(timezone=True),
           server_default=text("TIMEZONE('utc', now())"))
)
