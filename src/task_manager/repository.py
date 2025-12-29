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
