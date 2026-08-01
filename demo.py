from datetime import datetime
from context_engine.loader import load_scenario, get_raw_doc_size
from context_engine.planner import plan_context
from context_engine.retriever import retrieve
from context_engine.working_memory import create_working_memory, reset_working_memory
from context_engine.engine import process_documents
from context_engine.policy import evaluate
from context_engine.brief import create_decision_brief


def run_scenario(scenario_id: int) -> None:
    print(f"\n{'='*60}")
    print(f"SCENARIO {scenario_id}")
    print(f"{'='*60}\n")
    
    working_memory = create_working_memory()
    
    try:
        task, documents, allowed_documents, restricted_documents = load_scenario(scenario_id)
        
        print(f"Task: {task.metadata.description}")
        print(f"Documents loaded: {len(documents)}")
        print(f"Allowed documents: {allowed_documents}")
        print(f"Restricted documents: {restricted_documents}")
        
        required_context = plan_context(task)
        print(f"\nRequired context: {required_context}")
        
        retrieved = retrieve(required_context, documents, top_k=100)
        print(f"Retrieved documents: {len(retrieved)}")
        
        retrieved_docs = [r.document for r in retrieved]
        
        reference_date = datetime(2026, 1, 15)
        
        validated_evidence, stale_evidence, permission_violations, conflicts = process_documents(
            retrieved_docs,
            working_memory,
            allowed_documents,
            restricted_documents,
            reference_date
        )
        
        print(f"\nValidated evidence: {len(validated_evidence)}")
        print(f"Stale evidence: {len(stale_evidence)}")
        print(f"Permission violations: {len(permission_violations)}")
        print(f"Conflicts: {len(conflicts)}")
        
        decision = evaluate(validated_evidence, required_context, conflicts, stale_evidence, permission_violations)
        
        missing = []
        for category in required_context:
            found = False
            for e in validated_evidence:
                from context_engine.policy import _matches_category
                if _matches_category(e.claim, category):
                    found = True
                    break
            if not found:
                missing.append(category)
        
        raw_doc_size = get_raw_doc_size(documents)
        brief = create_decision_brief(
            decision=decision,
            evidence=validated_evidence,
            working_memory=working_memory,
            missing=missing,
            conflicts=conflicts,
            stale=stale_evidence,
            permission_violations=permission_violations,
            raw_doc_size=raw_doc_size
        )
        
        print(f"\n{'='*60}")
        print(f"DECISION BRIEF")
        print(f"{'='*60}")
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
        
    finally:
        reset_working_memory(working_memory)


def main():
    print("\n" + "="*60)
    print("EVIDENCE CONTEXT ENGINE - DEMO")
    print("="*60)
    
    for scenario_id in range(1, 5):
        run_scenario(scenario_id)
    
    print("\nDemo complete.")


if __name__ == "__main__":
    main()
