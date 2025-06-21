class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        self.tasks.append({"description": description, "done": False})

    def remove_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)

    def toggle_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = True

    def list_tasks(self):
        for i, task in enumerate(self.tasks):
            status = "[x]" if task["done"] else "[ ]"
            return f"{i}. {status} {task['description']}"

    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task["done"]]
