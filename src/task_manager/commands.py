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
'''class CreateTaskCommand(Command):
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
        self.manager.delete_task(self.task_id)'''

class CreateTaskCommand(Command):
    def __init__(
        self,
        manager: TaskManager,
        title: str,
        description: str = "",
        due=None,
        priority: int = 3,
        tags=None,
        project: Optional[str] = None,
    ):
        self.manager = manager
        self.title = title
        self.description = description
        self.due = due
        self.priority = priority
        self.tags = tags or []
        self.project = project
        self.task_id: Optional[str] = None

    def execute(self) -> None:
        task = self.manager.create_task(
            title=self.title,
            description=self.description,
            due=self.due,
            priority=self.priority,
            tags=self.tags,
            project_name=self.project,
        )
        self.task_id = task.id

    def undo(self) -> None:
        if self.task_id is None:
            raise BusinessError("No task to undo")
        self.manager.delete_task(self.task_id)


class UpdateTaskCommand(Command):
    def __init__(self, manager: TaskManager, task_id: str, new_title: str):
        self.manager = manager
        self.task_id = task_id
        self.new_title = new_title
        self.old_title: Optional[str] = None

    def execute(self) -> None:
        task = self.manager.get_task(self.task_id)
        self.old_title = task.title
        self.manager.update_task(self.task_id, self.new_title)

    def undo(self) -> None:
        if self.old_title is None:
            raise BusinessError("No update to undo")
        self.manager.update_task(self.task_id, self.old_title)
class CompleteTaskCommand(Command):
    def __init__(self, manager: TaskManager, task_id: str):
        self.manager = manager
        self.task_id = task_id
        self.was_completed: Optional[bool] = None

    def execute(self) -> None:
        task = self.manager.get_task(self.task_id)
        self.was_completed = task.completed
        self.manager.complete_task(self.task_id)

    def undo(self) -> None:
        if self.was_completed is False:
            self.manager.uncomplete_task(self.task_id)
class DeleteTaskCommand(Command):
    def __init__(self, manager: TaskManager, task_id: str):
        self.manager = manager
        self.task_id = task_id
        self.backup_task: Optional[Task] = None

    def execute(self) -> None:
        task = self.manager.get_task(self.task_id)
        self.backup_task = task
        self.manager.delete_task(self.task_id)

    def undo(self) -> None:
        if self.backup_task is None:
            raise BusinessError("No delete to undo")
        self.manager.restore_task(self.backup_task)
