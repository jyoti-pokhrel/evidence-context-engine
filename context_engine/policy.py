from dataclasses import dataclass
from typing import Literal
from schemas.evidence import Evidence, Conflict


@dataclass
class PolicyDecision:
    decision: Literal["PROCEED", "ESCALATE"]
    reason: str | None
    rules_fired: list[str]


def evaluate(
    evidence: list[Evidence],
    required_context: list[str],
    conflicts: list[Conflict],
    stale: list[Evidence] = None,
    permission_violations: list[Evidence] = None
) -> PolicyDecision:
    rules_fired = []
    
    if stale is None:
        stale = []
    if permission_violations is None:
        permission_violations = []
    
    missing = []
    for category in required_context:
        found = False
        for e in evidence:
            if _matches_category(e.claim, category):
                found = True
                break
        if not found:
            missing.append(category)
    
    if missing:
        rules_fired.append("Missing Evidence Rule")
        return PolicyDecision(
            decision="ESCALATE",
            reason=f"Missing required context: {', '.join(missing)}",
            rules_fired=rules_fired
        )
    
    unresolved_conflicts = [c for c in conflicts if not c.resolved]
    if unresolved_conflicts:
        rules_fired.append("Conflict Rule")
        return PolicyDecision(
            decision="ESCALATE",
            reason="Unresolved conflicting evidence",
            rules_fired=rules_fired
        )
    
    stale_for_required = []
    for e in stale:
        for category in required_context:
            if _matches_category(e.claim, category):
                stale_for_required.append(e)
                break
    
    if stale_for_required:
        rules_fired.append("Freshness Rule")
        return PolicyDecision(
            decision="ESCALATE",
            reason="Stale documentation for required context",
            rules_fired=rules_fired
        )
    
    permission_violations_for_required = []
    for e in permission_violations:
        for category in required_context:
            if _matches_category(e.claim, category):
                permission_violations_for_required.append(e)
                break
    
    if permission_violations_for_required:
        rules_fired.append("Permission Rule")
        return PolicyDecision(
            decision="ESCALATE",
            reason="Insufficient authorized evidence",
            rules_fired=rules_fired
        )
    
    rules_fired.append("Proceed Rule")
    return PolicyDecision(
        decision="PROCEED",
        reason="All required evidence validated",
        rules_fired=rules_fired
    )


def _matches_category(claim, category: str) -> bool:
    topic = claim.topic.lower()
    text = claim.text.lower()
    source = claim.source.lower()
    
    if category == "endpoint_implementation":
        return topic in ["api_structure", "general"] or "endpoint" in text or "login" in text or "login" in source
    elif category == "middleware":
        return topic == "middleware" or "middleware" in text or "middleware" in source
    elif category == "api_documentation":
        return topic == "api_structure" or "api" in text or "api" in source
    elif category == "security_policy":
        return topic == "authentication_method" or "authentication" in text or "security" in text or "security" in source
    elif category == "configuration":
        return topic == "configuration" or "config" in text or "config" in source or "rate_limit" in text
    else:
        return False
