
from datetime import datetime, date
import json
from user import User, Task

FILEPATH = "data/sample_data.json"


def save(user: User, file_path: str = FILEPATH) -> None:
    user_data = user.to_dict()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def load_user(file_path = FILEPATH) -> User:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return User(data['streaks'], load_tasks(data['tasks']), load_tasks(data['finished_tasks']), data['finished_tutorial'])

def load_tasks(data: list):
    return [Task(task['description'], datetime.strptime(task['deadline'], "%Y-%m-%d")) for task in data]
