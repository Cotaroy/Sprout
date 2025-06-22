
from __future__ import annotations

from dataclasses import dataclass, field
import datetime

import threading

def run_at_midnight(func):
    def schedule():
        while True:
            now = datetime.datetime.now()
            # Calculate next midnight
            next_midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_midnight = (next_midnight - now).total_seconds()
            threading.Event().wait(seconds_until_midnight)
            func()
    threading.Thread(target=schedule, daemon=True).start()



@dataclass
class User:
    streaks: int = 0
    event_index: int = 0
    finished_task_today: bool = False
    tasks: list[Task] = field(default_factory=list)
    finished_tasks: list[Task] = field(default_factory=list)
    finished_tutorial: bool = False
    recently_deleted: list[Task] = field(default_factory=list)

    def check_streak(self):
        if not self.finished_task_today and self.streaks > 0:
            self.streaks -= 1


    def to_dict(self):
        tasks = [task.to_dict() for task in self.tasks]
        finished_tasks = [task.to_dict() for task in self.finished_tasks]
        return {'streaks': self.streaks, 'event_index': self.event_index, 'finished_task_today': self.finished_task_today, 'tasks': tasks,
                'finished_tasks': finished_tasks, 'finished_tutorial': self.finished_tutorial}

    def complete_task(self, index):
        self.tasks[index].completed_date = datetime.datetime.today()
        self.finished_tasks.append(self.tasks.pop(index))
        if not self.finished_task_today:
            self.finished_task_today = True
            self.streaks += 1

    def delete_task(self, index):
        self.finished_tasks.pop(index)

    def restore_task(self, index):
        self.tasks.append(self.finished_tasks.pop(index))

@dataclass
class Task:
    description: str
    deadline: datetime.date
    completed_date: datetime.date = None

    def __hash__(self):
        return hash(self.description)

    def to_dict(self):
        if self.completed_date is not None:
            return {
                'description': self.description,
                'deadline': self.deadline.strftime("%Y-%m-%d"),
                'completed_date': self.completed_date.strftime("%Y-%m-%d")
            }
        else:
            return {
                'description': self.description,
                'deadline': self.deadline.strftime("%Y-%m-%d"),
                'completed_date': None
            }
