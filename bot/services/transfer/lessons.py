from models.lesson import Subject
from models.student import StudentSellOffer

from dataclasses import dataclass


@dataclass
class LessonCompleteResult:
    for_paid: bool = False
    paid_total_now: bool = False
    paid_offer: bool = False
    low_balance_student: bool = False

    seller_id: int = None
    worker_id: int = None
    subject: Subject = None
    offer: StudentSellOffer = None
