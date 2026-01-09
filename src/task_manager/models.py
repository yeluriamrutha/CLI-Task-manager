from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid

VALID_STATUSES = {"open", "in-progress", "done"}

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    due: Optional[datetime] = None
    priority: int = 3  # 1-high .. 5-low
    status: str = "open"  # open, in-progress, done
    tags: List[str] = field(default_factory=list)
    deps: List[str] = field(default_factory=list)  # dependency task ids

    def mark_done(self):
        self.status = "done"

    @property
    def due_date(self) -> Optional[datetime]:
        return self.due

    @due_date.setter
    def due_date(self, value: Optional[datetime]) -> None:
        self.due = value

    def to_dict(self):
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["due"] = self.due.isoformat() if self.due else None
        return d

    @classmethod
    def from_dict(cls, d):
        dd = dict(d)
        dd["created_at"] = datetime.fromisoformat(dd["created_at"])
        dd["due"] = datetime.fromisoformat(dd["due"]) if dd.get("due") else None
        return cls(**dd)

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("title must be non-empty")
        if not (1 <= self.priority <= 5):
            raise ValueError("priority must be between 1 and 5")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        if not isinstance(self.tags, list):
            raise ValueError("tags must be a list")

@dataclass
class Project:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task_ids: List[str] = field(default_factory=list)

    def add_task(self, task: Task):
        if task.id not in self.task_ids:
            self.task_ids.append(task.id)

    def remove_task(self, task_id: str):
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "task_ids": self.task_ids}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d.get("id", str(uuid.uuid4())), name=d["name"], task_ids=d.get("task_ids", []))