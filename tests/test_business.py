from task_manager.repository import InMemoryRepository
from task_manager.service import TaskManager, BusinessError
from task_manager.models import Task, Project

def test_dependencies_block_completion():
    repo = InMemoryRepository()
    mgr = TaskManager(repo)
    t1 = mgr.create_task("Task 1")
    t2 = mgr.create_task("Task 2")
    # make t2 depend on t1
    t2.deps = [t1.id]
    repo.save_task(t2)
    ok, blocking = mgr.can_complete(t2.id)
    assert not ok
    assert blocking == [t1.id]
    try:
        mgr.mark_complete(t2.id)
        assert False, "Should have raised BusinessError"
    except BusinessError:
        pass

def test_complete_after_deps_done():
    repo = InMemoryRepository()
    mgr = TaskManager(repo)
    t1 = mgr.create_task("T1")
    t2 = mgr.create_task("T2")
    t2.deps = [t1.id]
    repo.save_task(t2)
    # complete t1
    mgr.mark_complete(t1.id)
    # now t2 can be completed
    mgr.mark_complete(t2.id)
    assert repo.get_task(t2.id).status == "done"

def test_delete_task_removes_from_project():
    repo = InMemoryRepository()
    mgr = TaskManager(repo)
    p = repo.list_projects()  # empty
    t = mgr.create_task("T", project_name="P1")
    # project exists
    proj = repo.find_project_by_name("P1")
    assert proj is not None
    assert t.id in proj.task_ids
    # now delete task
    mgr.delete_task(t.id)
    proj2 = repo.get_project(proj.id)
    assert proj2 is not None
    assert t.id not in proj2.task_ids
    assert repo.get_task(t.id) is None