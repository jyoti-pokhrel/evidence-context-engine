from context_engine.pipeline import run_scenario_pipeline


def run_scenario(scenario_id: int) -> None:
    print(f"\n{'='*60}")
    print(f"SCENARIO {scenario_id}")
    print(f"{'='*60}\n")
    
    brief = run_scenario_pipeline(scenario_id)
    
    print(f"Decision: {brief.decision}")
    print(f"Reason: {brief.reason}")
    print(f"Rules fired: {brief.rules_fired}")
    print(f"Context reduction: {brief.context_reduction:.1%}")
    print(f"Evidence count: {len(brief.evidence)}")
    print(f"Working memory facts: {len(brief.working_memory.facts)}")
    
    if brief.missing:
        print(f"Missing: {brief.missing}")
    if brief.conflicts:
        print(f"Conflicts: {len(brief.conflicts)}")
    if brief.stale:
        print(f"Stale: {len(brief.stale)}")
    if brief.permission_violations:
        print(f"Permission violations: {len(brief.permission_violations)}")
    
    print(f"\n{'='*60}\n")
    
    return brief


def main():
    print("\n" + "="*60)
    print("EVIDENCE CONTEXT ENGINE - DEMO")
    print("="*60)
    
    for scenario_id in range(1, 5):
        run_scenario(scenario_id)
    
    print("\nDemo complete.")


if __name__ == "__main__":
    main()
