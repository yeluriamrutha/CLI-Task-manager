import os
from click.testing import CliRunner
from task_manager import cli
from task_manager.storage import SQLiteStorage

def test_cli_update_and_delete(tmp_path, monkeypatch):
    db_file = tmp_path / "cli_ud.db"
    monkeypatch.setattr(cli, "storage", SQLiteStorage(str(db_file)))
    # update manager uses storage set in cli module; re-import manager if needed
    runner = CliRunner()
    # create task
    r1 = runner.invoke(cli.cli, ["create-task", "--title", "ToUpdate"])
    assert r1.exit_code == 0
    # find the created task id
    tasks_out = runner.invoke(cli.cli, ["list-tasks"])
    assert "ToUpdate" in tasks_out.output
    # parse id: list-tasks shows id[:8] so we need to list storage directly
    # fallback: get id by querying storage
    task_list = cli.storage.list_tasks()
    assert len(task_list) == 1
    task_id = task_list[0].id
    # update title
    r2 = runner.invoke(cli.cli, ["update-task", task_id, "--title", "UpdatedTitle"])
    assert r2.exit_code == 0
    out = runner.invoke(cli.cli, ["show-task", task_id])
    assert "UpdatedTitle" in out.output
    # delete
    r3 = runner.invoke(cli.cli, ["delete-task", task_id])
    assert r3.exit_code == 0
    out2 = runner.invoke(cli.cli, ["show-task", task_id])
    assert "not found" in out2.output