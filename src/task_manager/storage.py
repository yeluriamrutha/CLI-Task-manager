import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

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
                INSERT OR REPLACE INTO tasks
                (id, title, status, due_date, project, tags)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.status,
                    task.due.isoformat() if task.due else None,
                    None,
                    ",".join(task.tags),
                ),
            )    



    def get_task(self, task_id: str) -> Optional[Task]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, status, due_date, tags FROM tasks WHERE id = ?",
                (task_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            return Task(
                id=row[0],
                title=row[1],
                status=row[2],
                due=datetime.fromisoformat(row[3]) if row[3] else None,
                tags=row[4].split(",") if row[4] else [],
            )


    def list_tasks(self) -> List[Task]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, status, due_date, tags FROM tasks"
            )
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                tasks.append(
                    Task(
                        id=row[0],
                        title=row[1],
                        status=row[2],
                        due=datetime.fromisoformat(row[3]) if row[3] else None,
                        tags=row[4].split(",") if row[4] else [],
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

    def list_projects(self) -> List[Project]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name FROM projects"
                )
            rows = cursor.fetchall()
                
            projects = []
            for row in rows:
                cursor.execute(
                    "SELECT id FROM tasks WHERE project = ?",
                    (row[0],)
                )
                task_ids = [r[0] for r in cursor.fetchall()]
                projects.append(
                    Project(
                        id=row[0],
                        name=row[1],
                        task_ids=task_ids,
                    )
                )
            return projects
    
    def delete_task(self, task_id: str) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

