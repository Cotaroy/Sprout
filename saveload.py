
import datetime
import json
from user import User, Task

FILEPATH = "data/sample_data.json"


def save(user: User, file_path: str = FILEPATH) -> None:
    user_data = user.to_dict()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def load_user(file_path = FILEPATH) -> User:
    """
    >>> a = Task('say hello to the neighbours', datetime.datetime.now().date())
    >>> tommy = User(tasks=[a])
    >>> save(tommy, 'data/test.json')
    >>> load_user('data/test.json')
    User(streaks=0, finished_task_today=False, tasks=[Task(description='say hello to the neighbours', deadline=datetime.datetime(2025, 6, 21, 0, 0))], finished_tasks=[], finished_tutorial=False, recently_deleted=[])

    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return User(data['streaks'], data['finished_task_today'], load_tasks(data['tasks']),
                load_tasks(data['finished_tasks']), data['finished_tutorial'])

def load_tasks(data: list):
    return [Task(task['description'], datetime.datetime.strptime(task['deadline'], "%Y-%m-%d")) for task in data]
