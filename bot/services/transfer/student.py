from dataclasses import dataclass


@dataclass
class StudentInitializingData:
    name: str
    city: str
    description: str
    default_rate: int
