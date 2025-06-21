from win32ctypes.pywin32.pywintypes import datetime

from datetime import datetime
from task import Task

SAMPLE_TASKS = [
    Task('hello', datetime.today())
] * 5


class Ivern:
    def __init__(self):
        self.growth = 0
        self.tasks = SAMPLE_TASKS
        self.completed_task = {}

    def complete_task(self, index):
        if self.tasks[index].description in self.completed_task:
            self.completed_task[self.tasks[index]] += 1
        else:
            self.completed_task[self.tasks[index]] = 1
        self.tasks.pop(index)

    def show_tasks(self):
        build = ""
        for task in self.tasks:
            build += f"[ ] \t {task.description} | {task.deadline} \n"
        return build
