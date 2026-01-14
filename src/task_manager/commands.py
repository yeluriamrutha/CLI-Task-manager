from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List

from .service import TaskManager, BusinessError
from .models import Task
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass
class UndoManager:
    def __init__(self) -> None:
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> None:
        if not self._undo_stack:
            raise BusinessError("Nothing to undo")
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self) -> None:
        if not self._redo_stack:
            raise BusinessError("Nothing to redo")
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
class CreateTaskCommand(Command):
    def __init__(self, manager: TaskManager, project: str, title: str):
        self.manager = manager
        self.project = project
        self.title = title
        self.task_id: Optional[str] = None

    def execute(self) -> None:
        task = self.manager.create_task(self.project, self.title)
        self.task_id = task.id

    def undo(self) -> None:
        if self.task_id is None:
            raise BusinessError("No task to undo")
        self.manager.delete_task(self.task_id)
