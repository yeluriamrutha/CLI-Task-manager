from __future__ import annotations
import click
import json
from datetime import datetime, date
from typing import Optional, List
from .models import Task, Project
from .storage import SQLiteStorage
from .service import TaskManager, BusinessError

from .commands import (
    UndoManager,
    CreateTaskCommand,
    UpdateTaskCommand,
    CompleteTaskCommand,
    DeleteTaskCommand,
)


# Default DB file in repo root (can be overridden in future)
storage: SQLiteStorage = SQLiteStorage("task_data.db")

undo_manager = UndoManager()


# manager: TaskManager = TaskManager(storage)
def get_manager() -> TaskManager:
    return TaskManager(storage)


@click.group()
def cli() -> None:
    """Task Manager CLI"""
    pass


def _parse_due(due_str: Optional[str]) -> Optional[datetime]:
    if not due_str:
        return None
    try:
        # Accept ISO format or YYYY-MM-DD
        return datetime.fromisoformat(due_str)
    except Exception:
        # try YYYY-MM-DD
        try:
            return datetime.fromisoformat(due_str + "T00:00:00")
        except Exception:
            return None


@cli.command("create-task")
@click.option("--title", required=True, help="Task title")
@click.option("--description", default="", help="Task description")
@click.option("--due", default=None, help="Due date (ISO format or YYYY-MM-DD)")
@click.option("--priority", default=3, type=int, help="Priority 1 (high) .. 5 (low)")
@click.option("--tag", "-t", multiple=True, help="Tag(s) for the task")
@click.option("--project", default=None, help="Project name to add the task to")
def create_task(
    title: str,
    description: str,
    due: Optional[str],
    priority: int,
    tag: tuple,
    project: Optional[str],
) -> None:
    due_dt = _parse_due(due)
    try:
        '''t = get_manager().create_task(
            title=title,
            description=description,
            due=due_dt,
            priority=priority,
            tags=list(tag),
            project_name=project,
        )
        click.echo(f"Created task {t.id} | {t.title}")'''

        manager = get_manager()
        cmd = CreateTaskCommand(
            manager,
            title=title,
            description=description,
            due=due_dt,
            priority=priority,
            tags=list(tag),
            project=project,
        )
        undo_manager.execute(cmd)

        click.echo("Task created (undo available)")


    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command("update-task")
@click.argument("task_id")
@click.option("--title", default=None)
@click.option("--description", default=None)
@click.option("--due", default=None)
@click.option("--priority", default=None, type=int)
@click.option("--status", default=None)
@click.option("--tag", "tags", multiple=True)
def update_task(
    task_id: str,
    title: Optional[str],
    description: Optional[str],
    due: Optional[str],
    priority: Optional[int],
    status: Optional[str],
    tags: tuple,
) -> None:
    fields = {}
    if title is not None:
        fields["title"] = title
    if description is not None:
        fields["description"] = description
    if due is not None:
        fields["due"] = _parse_due(due)
    if priority is not None:
        fields["priority"] = priority
    if status is not None:
        fields["status"] = status
    if tags:
        fields["tags"] = list(tags)
    try:
        t = get_manager().update_task(task_id, **fields)
        click.echo(f"Updated task {t.id} | {t.title}")
    except BusinessError as e:
        click.echo(f"Business error: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command("list-tasks")
@click.option("--project", default=None, help="Filter tasks by project name")
@click.option("--tag", default=None, help="Filter by tag")
@click.option(
    "--due-before",
    default=None,
    help="Show tasks due on or before this date (YYYY-MM-DD or ISO)",
)
@click.option(
    "--overdue",
    is_flag=True,
    default=False,
    help="Show overdue tasks (due < today and not done)",
)
def list_tasks(
    project: Optional[str], tag: Optional[str], due_before: Optional[str], overdue: bool
) -> None:
    # tasks = storage.list_tasks()
    tasks = get_manager().list_tasks()

    # project filter
    if project:
        p = storage.find_project_by_name(project)
        if not p:
            click.echo(f"No project named '{project}'")
            return
        tasks = [t for t in tasks if t.id in p.task_ids]
    # tag filter
    if tag:
        tasks = [t for t in tasks if tag in t.tags]
    # due-before filter
    if due_before:
        db_dt = _parse_due(due_before)
        if db_dt:
            tasks = [t for t in tasks if t.due and t.due <= db_dt]
    # overdue filter
    if overdue:
        today = datetime.utcnow().date()
        tasks = [
            t for t in tasks if t.due and t.status != "done" and t.due.date() < today
        ]

    if not tasks:
        click.echo("No tasks.")
        return

    for t in sorted(tasks, key=lambda x: (x.status, x.priority)):
        due_str = t.due.isoformat() if t.due else "—"
        click.echo(
            f"{t.id[:8]} | {t.title} | {t.status} | due:{due_str} | prio:{t.priority} | tags:{','.join(t.tags)}"
        )


@cli.command("show-task")
@click.argument("task_id")
def show_task(task_id: str) -> None:
    t = storage.get_task(task_id)
    if not t:
        click.echo(f"Task {task_id} not found")
        return
    click.echo(json.dumps(t.to_dict(), indent=2))


@cli.command("complete-task")
@click.argument("task_id")
def complete_task(task_id: str) -> None:
    try:
        _ = get_manager().mark_complete(task_id)
        click.echo(f"Marked {task_id} as done")
    except BusinessError as e:
        click.echo(f"Cannot complete task: {e}")


@cli.command("delete-task")
@click.argument("task_id")
def delete_task(task_id: str) -> None:
    try:
        get_manager().delete_task(task_id)
        click.echo(f"Deleted task {task_id}")
    except BusinessError as e:
        click.echo(f"Cannot delete task: {e}")


@cli.command("create-project")
@click.option("--name", required=True, help="Project name")
def create_project(name: str) -> None:
    existing = storage.find_project_by_name(name)
    if existing:
        click.echo(f"Project '{name}' already exists (id={existing.id})")
        return
    p = Project(name=name)
    storage.save_project(p)
    click.echo(f"Created project {p.id} | {p.name}")


@cli.command("list-projects")
def list_projects() -> None:
    for p in storage.list_projects():
        click.echo(f"{p.id[:8]} | {p.name} | tasks:{len(p.task_ids)}")

@cli.command("undo")
def undo() -> None:
    try:
        undo_manager.undo()
        click.echo("Last action undone")
    except BusinessError as e:
        click.echo(str(e))

@cli.command("redo")
def redo() -> None:
    try:
        undo_manager.redo()
        click.echo("Last action redone")
    except BusinessError as e:
        click.echo(str(e))


if __name__ == "__main__":
    cli()
