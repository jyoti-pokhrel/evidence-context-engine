from schemas.decision_brief import DecisionBrief
from schemas.evidence import Evidence, Conflict
from schemas.working_memory import WorkingMemory
from context_engine.policy import PolicyDecision


def create_decision_brief(
    decision: PolicyDecision,
    evidence: list[Evidence],
    working_memory: WorkingMemory,
    missing: list[str],
    conflicts: list[Conflict],
    stale: list[Evidence],
    permission_violations: list[Evidence],
    raw_doc_size: int
) -> DecisionBrief:
    brief_size = _estimate_brief_size(evidence, working_memory, missing, conflicts, stale, permission_violations)
    context_reduction = max(0.0, min(1.0, 1.0 - (brief_size / raw_doc_size))) if raw_doc_size > 0 else 0.0
    
    return DecisionBrief(
        decision=decision.decision,
        reason=decision.reason,
        evidence=evidence,
        working_memory=working_memory,
        missing=missing,
        conflicts=conflicts,
        stale=stale,
        permission_violations=permission_violations,
        rules_fired=decision.rules_fired,
        context_reduction=context_reduction
    )


def _estimate_brief_size(
    evidence: list[Evidence],
    working_memory: WorkingMemory,
    missing: list[str],
    conflicts: list[Conflict],
    stale: list[Evidence],
    permission_violations: list[Evidence]
) -> int:
    """
    Estimate the size of the compressed context in the Decision Brief.
    
    Only counts validated evidence and working memory facts (what's retained),
    not diagnostic metadata like stale, violations, conflicts, or missing
    (what's rejected). A brief that correctly identifies and excludes stale
    claims should get credit for that exclusion, not be penalized by including
    their text length in the "compressed" size.
    """
    size = 0
    for e in evidence:
        size += len(e.claim.text) + len(e.claim.source)
    for fact in working_memory.facts:
        size += len(fact.key) + len(fact.value)
    return size
