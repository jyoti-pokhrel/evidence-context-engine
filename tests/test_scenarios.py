from context_engine.loader import load_scenario
from context_engine.pipeline import run_scenario_pipeline


def test_load_scenario_1():
    task, documents, allowed, restricted = load_scenario(1)
    
    assert task.metadata.task_type == "rate_limiting"
    assert len(documents) > 0
    assert len(allowed) > 0
    assert len(restricted) == 0


def test_load_scenario_2():
    task, documents, allowed, restricted = load_scenario(2)
    
    assert task.metadata.task_type == "rate_limiting"
    assert len(documents) > 0


def test_load_scenario_3():
    task, documents, allowed, restricted = load_scenario(3)
    
    assert task.metadata.task_type == "rate_limiting"
    assert len(documents) > 0
    assert len(restricted) > 0


def test_load_scenario_4():
    task, documents, allowed, restricted = load_scenario(4)
    
    assert task.metadata.task_type == "rate_limiting"
    assert len(documents) > 0


def test_scenario_1_proceeds():
    """Scenario 1: All evidence present, fresh, authorized. Should PROCEED."""
    brief = run_scenario_pipeline(1)
    
    assert brief.decision == "PROCEED"
    assert brief.rules_fired == ["Proceed Rule"]
    assert len(brief.evidence) > 0
    assert len(brief.missing) == 0
    assert len(brief.conflicts) == 0
    assert len(brief.stale) == 0
    assert len(brief.permission_violations) == 0


def test_scenario_2_escalates_on_staleness():
    """Scenario 2: Architecture doc is stale (>12 months old). Should ESCALATE."""
    brief = run_scenario_pipeline(2)
    
    assert brief.decision == "ESCALATE"
    assert "Freshness Rule" in brief.rules_fired
    assert len(brief.stale) > 0
    assert brief.reason == "Stale documentation for required context"


def test_scenario_3_escalates_on_permissions():
    """Scenario 3: Security policy is restricted. Should ESCALATE."""
    brief = run_scenario_pipeline(3)
    
    assert brief.decision == "ESCALATE"
    assert "Permission Rule" in brief.rules_fired
    assert len(brief.permission_violations) > 0
    assert brief.reason == "Insufficient authorized evidence"


def test_scenario_4_escalates_on_conflict():
    """Scenario 4: Two architecture docs conflict on auth method (equal authority). Should ESCALATE."""
    brief = run_scenario_pipeline(4)
    
    assert brief.decision == "ESCALATE"
    assert "Conflict Rule" in brief.rules_fired
    assert len(brief.conflicts) > 0
    unresolved = [c for c in brief.conflicts if not c.resolved]
    assert len(unresolved) > 0
    assert brief.reason == "Unresolved conflicting evidence"
