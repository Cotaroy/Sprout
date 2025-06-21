
from __future__ import annotations

from dataclasses import dataclass, field
import datetime


@dataclass
class User:
    streaks: int = 0
    tasks: list[Task] = field(default_factory=list)
    finished_tasks: list[Task] = field(default_factory=list)
    finished_tutorial: bool = False

    def to_dict(self):
        tasks = [task.to_dict() for task in self.tasks]
        finished_tasks = [task.to_dict() for task in self.finished_tasks]
        return {'streaks': self.streaks, 'tasks': tasks,
                'finished_tasks': finished_tasks, 'finished_tutorial': self.finished_tutorial}

@dataclass
class Task:
    description: str
    deadline: datetime.datetime

    def __hash__(self):
        return hash(self.description)

    def to_dict(self):
        return {'description': self.description, 'deadline': str(self.deadline)}
