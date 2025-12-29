from task_manager.models import Task


def test_task_mark_done():
    t = Task(title="Write tests")
    assert t.status == "open"
    t.mark_done()
    assert t.status == "done"
