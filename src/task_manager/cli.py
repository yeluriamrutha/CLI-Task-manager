import click
import json
from datetime import datetime
from typing import Optional
from .models import Task, Project
from .storage import SQLiteStorage
from .service import TaskManager, BusinessError

# Shared storage and manager (IMPORTANT)
storage = SQLiteStorage("task_data.db")

def get_manager():
    return TaskManager(storage)



@click.group()
def cli():
    """Task Manager CLI"""
    pass


def _parse_due(due_str: Optional[str]) -> Optional[datetime]:
    if not due_str:
        return None
    try:
        return datetime.fromisoformat(due_str)
    except Exception:
        return None


@cli.command("create-task")
@click.option("--title", required=True, help="Task title")
@click.option("--description", default="", help="Task description")
@click.option("--due", default=None, help="Due date (ISO format or YYYY-MM-DD)")
@click.option("--priority", default=3, type=int, help="Priority 1 (high) .. 5 (low)")
@click.option("--tag", "-t", multiple=True, help="Tag(s) for the task")
@click.option("--project", default=None, help="Project name to add the task to")
def create_task(title, description, due, priority, tag, project):
    due_dt = _parse_due(due)
    try:
        t = get_manager().create_task(
            title=title,
            description=description,
            due=due_dt,
            priority=priority,
            tags=list(tag),
            project_name=project,
        )
        click.echo(f"Created task {t.id} | {t.title}")
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
def update_task(task_id, title, description, due, priority, status, tags):
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
def list_tasks(project, tag):
    # ✅ FIX: use TaskManager, not storage
    tasks = get_manager().list_tasks()

    if project:
        p = get_manager().find_project_by_name(project)
        if not p:
            click.echo(f"No project named '{project}'")
            return
        tasks = [t for t in tasks if t.id in p.task_ids]

    if tag:
        tasks = [t for t in tasks if tag in t.tags]

    if not tasks:
        click.echo("No tasks.")
        return

    for t in sorted(tasks, key=lambda x: (x.status, x.priority)):
        due = t.due.isoformat() if t.due else "—"
        click.echo(
            f"{t.id[:8]} | {t.title} | {t.status} | due:{due} | prio:{t.priority}"
        )


@cli.command("show-task")
@click.argument("task_id")
def show_task(task_id):
    # ✅ FIX: use TaskManager, not storage
    t = get_manager().get_task(task_id)
    if not t:
        click.echo(f"Task {task_id} not found")
        return
    click.echo(json.dumps(t.to_dict(), indent=2))


@cli.command("complete-task")
@click.argument("task_id")
def complete_task(task_id):
    try:
        get_manager().mark_complete(task_id)
        click.echo(f"Marked {task_id} as done")
    except BusinessError as e:
        click.echo(f"Cannot complete task: {e}")


@cli.command("delete-task")
@click.argument("task_id")
def delete_task(task_id):
    try:
        get_manager().delete_task(task_id)
        click.echo(f"Deleted task {task_id}")
    except BusinessError as e:
        click.echo(f"Cannot delete task: {e}")


@cli.command("create-project")
@click.option("--name", required=True, help="Project name")
def create_project(name):
    existing = get_manager().find_project_by_name(name)
    if existing:
        click.echo(f"Project '{name}' already exists (id={existing.id})")
        return
    p = Project(name=name)
    storage.save_project(p)
    click.echo(f"Created project {p.id} | {p.name}")


@cli.command("list-projects")
def list_projects():
    for p in storage.list_projects():
        click.echo(f"{p.id[:8]} | {p.name} | tasks:{len(p.task_ids)}")


if __name__ == "__main__":
    cli()
