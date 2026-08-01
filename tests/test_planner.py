from context_engine.planner import plan_context
from schemas.task import Task, TaskMetadata


def test_plan_context_rate_limiting():
    task = Task(
        metadata=TaskMetadata(
            task_id="test-001",
            task_type="rate_limiting",
            description="Add rate limiting to /login"
        )
    )
    
    required = plan_context(task)
    
    assert "endpoint_implementation" in required
    assert "middleware" in required
    assert "api_documentation" in required
    assert "security_policy" in required
    assert "configuration" in required


def test_plan_context_unknown_type():
    task = Task(
        metadata=TaskMetadata(
            task_id="test-002",
            task_type="unknown_type",
            description="Unknown task"
        )
    )
    
    required = plan_context(task)
    
    assert len(required) > 0
