from context_engine.loader import load_scenario


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
