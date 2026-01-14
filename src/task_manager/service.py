from __future__ import annotations
from typing import List, Optional, Tuple
from .models import Task, Project
from .repository import Repository
from datetime import datetime


class BusinessError(Exception):
    """Raised for domain/business rule violations."""


class TaskManager:
    def __init__(self, repo: Repository):
        self.repo = repo

    def create_task(
        self,
        title: str,
        description: str = "",
        due: Optional[datetime] = None,
        priority: int = 3,
        tags: Optional[List[str]] = None,
        project_name: Optional[str] = None,
    ) -> Task:
        tags = list(tags or [])
        t = Task(
            title=title, description=description, due=due, priority=priority, tags=tags
        )
        t.validate()  # ensure basic validation before save
        self.repo.save_task(t)
        if project_name:
            p = (
                self.repo.find_project_by_name(project_name)
                if hasattr(self.repo, "find_project_by_name")
                else None
            )
            if p:
                p.add_task(t)
                self.repo.save_project(p)
            else:
                p = Project(name=project_name, task_ids=[t.id])
                self.repo.save_project(p)
        return t

    def update_task(self, task_id: str, **fields) -> Task:
        t = self.repo.get_task(task_id)
        if not t:
            raise BusinessError(f"Task {task_id} not found")
        # only allow certain fields to be updated
        allowed = {"title", "description", "due", "priority", "tags", "deps", "status"}
        for k, v in fields.items():
            if k not in allowed:
                continue
            setattr(t, k, v)
        t.validate()
        self.repo.save_task(t)
        return t

    def list_tasks(self):
        return self.repo.list_tasks()

    def _blocking_dependencies(self, task: Task) -> List[str]:
        """Return list of dependency IDs that are not done or missing."""
        blocking = []
        for dep_id in task.deps:
            dep = self.repo.get_task(dep_id)
            if not dep or dep.status != "done":
                blocking.append(dep_id)
        return blocking

    def can_complete(self, task_id: str) -> Tuple[bool, List[str]]:
        t = self.repo.get_task(task_id)
        if not t:
            raise BusinessError(f"Task {task_id} not found")
        blocking = self._blocking_dependencies(t)
        return (len(blocking) == 0, blocking)

    def mark_complete(self, task_id: str) -> Task:
        t = self.repo.get_task(task_id)
        if not t:
            raise BusinessError(f"Task {task_id} not found")
        ok, blocking = self.can_complete(task_id)
        if not ok:
            raise BusinessError(f"Cannot complete task; blocking deps: {blocking}")
        t.mark_done()
        self.repo.save_task(t)
        return t

    def delete_task(self, task_id: str) -> None:
        # remove references from projects
        for p in self.repo.list_projects():
            if task_id in p.task_ids:
                p.remove_task(task_id)
                self.repo.save_project(p)
        # delete task record
        if hasattr(self.repo, "delete_task"):
            self.repo.delete_task(task_id)
        else:
            raise BusinessError("Repository does not support delete_task")

    def project_stats(self, project_id: str) -> dict:
        p = self.repo.get_project(project_id)
        if not p:
            raise BusinessError(f"Project {project_id} not found")
        tasks = [
            self.repo.get_task(tid) for tid in p.task_ids if self.repo.get_task(tid)
        ]
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == "done")
        open_count = total - done
        return {"project": p.name, "total": total, "done": done, "open": open_count}

    def get_task(self, task_id: str) -> Task:
        task = self.repo.get_task(task_id)
        if task is None:
            raise BusinessError("Task not found")
        return task

    def uncomplete_task(self, task_id: str) -> None:
        task = self.get_task(task_id)
        task.completed = False
        self.repo.save_task(task)
        
    def restore_task(self, task: Task) -> None:
        self.repo.save_task(task)
