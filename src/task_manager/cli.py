import click
import json
from datetime import datetime
from typing import Optional
from .models import Project
from .storage import SQLiteStorage
from .service import TaskManager, BusinessError

# Global storage (will be monkeypatched in tests)
storage = SQLiteStorage("task_data.db")


def get_manager():
    # IMPORTANT: always build manager from CURRENT storage
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
def create_task(title):
    # DO NOT swallow exceptions (tests depend on real failure)
    t = get_manager().create_task(title=title)
    click.echo(f"Created task {t.id} | {t.title}")


@cli.command("update-task")
@click.argument("task_id")
@click.option("--title", default=None)
@click.option("--status", default=None)
def update_task(task_id, title, status):
    fields = {}
    if title is not None:
        fields["title"] = title
    if status is not None:
        fields["status"] = status

    t = get_manager().update_task(task_id, **fields)
    click.echo(f"Updated task {t.id} | {t.title}")


@cli.command("list-tasks")
def list_tasks():
    # READ directly from storage (test expects this)
    tasks = storage.list_tasks()

    if not tasks:
        click.echo("No tasks.")
        return

    for t in tasks:
        click.echo(f"{t.id[:8]} | {t.title} | {t.status}")


@cli.command("show-task")
@click.argument("task_id")
def show_task(task_id):
    t = storage.get_task(task_id)
    if not t:
        click.echo(f"Task {task_id} not found")
        return
    click.echo(json.dumps(t.to_dict(), indent=2))


@cli.command("complete-task")
@click.argument("task_id")
def complete_task(task_id):
    get_manager().mark_complete(task_id)
    click.echo(f"Marked {task_id} as done")


@cli.command("delete-task")
@click.argument("task_id")
def delete_task(task_id):
    get_manager().delete_task(task_id)
    click.echo(f"Deleted task {task_id}")


@cli.command("create-project")
@click.option("--name", required=True)
def create_project(name):
    p = Project(name=name)
    storage.save_project(p)
    click.echo(f"Created project {p.id} | {p.name}")


@cli.command("list-projects")
def list_projects():
    for p in storage.list_projects():
        click.echo(f"{p.id[:8]} | {p.name}")


if __name__ == "__main__":
    cli()
