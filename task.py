
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    description: str
    deadline: datetime.date

    def __hash__(self):
        return hash(self.description)
