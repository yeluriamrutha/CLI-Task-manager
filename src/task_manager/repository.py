from abc import ABC, abstractmethod
from typing import List
from .models import Task


class Repository(ABC):

    @abstractmethod
    def add_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def list_tasks(self) -> List[Task]:
        pass
class InMemoryRepository:
    def __init__(self):
        self.tasks = {}
        self.projects = {}

    # ---- Task methods ----
    def save_task(self, task):
        self.tasks[task.id] = task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def list_tasks(self):
        return list(self.tasks.values())

    def delete_task(self, task_id):
        self.tasks.pop(task_id, None)

    # ---- Project methods ----
    def save_project(self, project):
        self.projects[project.id] = project

    def get_project(self, project_id):
        return self.projects.get(project_id)

    def find_project_by_name(self, name):
        for p in self.projects.values():
            if p.name == name:
                return p
        return None

    def delete_project(self, project_id):
        self.projects.pop(project_id, None)
    
    def list_projects(self):
        return list(self.projects.values())
    
    def list_projects(self):
        return list(self.projects.values())


