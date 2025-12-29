from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_done(self) -> None:
        self.status = "done"
