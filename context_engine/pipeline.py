from datetime import datetime
from schemas.decision_brief import DecisionBrief
from context_engine.loader import load_scenario, get_raw_doc_size
from context_engine.planner import plan_context
from context_engine.retriever import retrieve
from context_engine.working_memory import create_working_memory, reset_working_memory
from context_engine.engine import process_documents
from context_engine.policy import evaluate, _matches_category
from context_engine.brief import create_decision_brief


def run_scenario_pipeline(scenario_id: int, reference_date: datetime = None) -> DecisionBrief:
    """
    Execute the full context engine pipeline for a given scenario.
    
    Args:
        scenario_id: The scenario number (1-4)
        reference_date: Optional reference date for freshness validation.
                       Defaults to 2026-01-15 if not provided.
    
    Returns:
        DecisionBrief: The complete decision brief with validated evidence,
                      conflicts, missing context, and decision.
    """
    if reference_date is None:
        reference_date = datetime(2026, 1, 15)
    
    working_memory = create_working_memory()
    
    task, documents, allowed_documents, restricted_documents = load_scenario(scenario_id)
    
    required_context = plan_context(task)
    
    retrieved = retrieve(required_context, documents, top_k=100)
    retrieved_docs = [r.document for r in retrieved]
    
    validated_evidence, stale_evidence, permission_violations, conflicts = process_documents(
        retrieved_docs,
        working_memory,
        allowed_documents,
        restricted_documents,
        reference_date
    )
    
    decision = evaluate(validated_evidence, required_context, conflicts, stale_evidence, permission_violations)
    
    missing = []
    for category in required_context:
        found = False
        for e in validated_evidence:
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
    
    return brief
