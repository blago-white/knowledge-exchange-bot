from dataclasses import dataclass


@dataclass(frozen=True)
class Worker:
    phone_number: str
    firstname: str
    lastname: str
    description: str
    meet_link: str

    bank_card_number: str | None
