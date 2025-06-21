
from __future__ import annotations

from dataclasses import dataclass, field
import datetime


@dataclass
class User:
    streaks: int = 0
    tasks: list[Task] = field(default_factory=list)
    finished_tasks: list[Task] = field(default_factory=list)
    finished_tutorial: bool = False
    recently_deleted: list[Task] = field(default_factory=list)

    def to_dict(self):
        tasks = [task.to_dict() for task in self.tasks]
        finished_tasks = [task.to_dict() for task in self.finished_tasks]
        return {'streaks': self.streaks, 'tasks': tasks,
                'finished_tasks': finished_tasks, 'finished_tutorial': self.finished_tutorial}

    def delete_task(self, index):
        self.recently_deleted.append(self.tasks.pop(index))

    def restore_task(self, index):
        self.tasks.append(self.recently_deleted.pop(index))

@dataclass
class Task:
    description: str
    deadline: datetime.datetime

    def __hash__(self):
        return hash(self.description)

    def to_dict(self):
        return {'description': self.description, 'deadline': str(self.deadline)}
