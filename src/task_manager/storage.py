import sqlite3
from pathlib import Path
from typing import List, Optional

from .models import Task, Project


class SQLiteStorage:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path("task_data.db")

        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_date TEXT,
                    project TEXT,
                    tags TEXT
                )
            """)

    def save_project(self, project: Project) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO projects (id, name) VALUES (?, ?)",
                (project.id, project.name),
            )

    def save_task(self, task: Task) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO tasks (id, title, status, due_date, project, tags)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.status,
                    task.due_date,
                    task.project,
                    ",".join(task.tags),
                ),
            )
            conn.commit()


    def get_task(self, task_id: str) -> Optional[Task]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, status, due_date, project, tags FROM tasks WHERE id = ?",
                (task_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return Task(
                id=row[0],
                title=row[1],
                status=row[2],
                due_date=row[3],
                project=row[4],
                tags=row[5].split(",") if row[5] else [],
            )

    def list_tasks(self) -> List[Task]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, status, due_date, project, tags FROM tasks"
            )
            rows = cursor.fetchall()

            tasks = []
            for row in rows:
                tasks.append(
                    Task(
                        id=row[0],
                        title=row[1],
                        status=row[2],
                        due_date=row[3],
                        project=row[4],
                        tags=row[5].split(",") if row[5] else [],
                    )
                )
            return tasks

    def complete_task(self, task_id: str) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = 'done' WHERE id = ?",
                (task_id,),
            )
    def delete_project(self, project_id: str) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE project = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))

