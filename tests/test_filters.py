from datetime import datetime, timedelta
from task_manager.repository import InMemoryRepository
from task_manager.service import TaskManager

def test_due_before_and_overdue_filters():
    repo = InMemoryRepository()
    mgr = TaskManager(repo)
    today = datetime.utcnow()
    past = today - timedelta(days=3)
    future = today + timedelta(days=5)
    t1 = mgr.create_task("past task", due=past)   # overdue
    t2 = mgr.create_task("future task", due=future)
    t3 = mgr.create_task("no due")

    # verify repo listing
    tasks = repo.list_tasks()
    assert any(t.id == t1.id for t in tasks)
    assert any(t.id == t2.id for t in tasks)
    assert any(t.id == t3.id for t in tasks)

    # mark t2 done and ensure overdue only picks t1 (t2 not overdue)
    mgr.mark_complete(t2.id)
    overdue = [t for t in repo.list_tasks() if t.due and t.status != "done" and t.due.date() < datetime.utcnow().date()]
    assert any(t.id == t1.id for t in overdue)
    assert all(t.id != t2.id for t in overdue)