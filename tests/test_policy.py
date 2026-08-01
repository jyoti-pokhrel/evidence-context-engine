from datetime import datetime
from context_engine.policy import evaluate
from schemas.evidence import Evidence, Claim, Conflict


def test_evaluate_proceed():
    claim = Claim(
        claim_id="test-1",
        text="Test claim",
        source="test.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    evidence = [Evidence(claim=claim)]
    required = ["security_policy"]
    
    decision = evaluate(evidence, required, [])
    
    assert decision.decision == "PROCEED"
    assert "Proceed Rule" in decision.rules_fired


def test_evaluate_missing_evidence():
    evidence = []
    required = ["security_policy"]
    
    decision = evaluate(evidence, required, [])
    
    assert decision.decision == "ESCALATE"
    assert "Missing Evidence Rule" in decision.rules_fired


def test_evaluate_unresolved_conflicts():
    claim_a = Claim(
        claim_id="test-1",
        text="Test A",
        source="doc1.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    claim_b = Claim(
        claim_id="test-2",
        text="Test B",
        source="doc2.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    evidence = [Evidence(claim=claim_a), Evidence(claim=claim_b)]
    required = ["security_policy"]
    conflicts = [Conflict(claim_a=evidence[0], claim_b=evidence[1], topic="authentication_method", resolved=False)]
    
    decision = evaluate(evidence, required, conflicts)
    
    assert decision.decision == "ESCALATE"
    assert "Conflict Rule" in decision.rules_fired


def test_evaluate_stale_evidence():
    valid_claim = Claim(
        claim_id="valid-1",
        text="Valid claim about authentication",
        source="valid.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    stale_claim = Claim(
        claim_id="test-1",
        text="Test claim about authentication",
        source="test.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2024, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    evidence = [Evidence(claim=valid_claim)]
    stale = [Evidence(claim=stale_claim)]
    required = ["security_policy"]
    
    decision = evaluate(evidence, required, [], stale)
    
    assert decision.decision == "ESCALATE"
    assert "Freshness Rule" in decision.rules_fired


def test_evaluate_permission_violations():
    valid_claim = Claim(
        claim_id="valid-1",
        text="Valid claim about authentication",
        source="valid.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    violation_claim = Claim(
        claim_id="test-1",
        text="Test claim about authentication",
        source="security.md",
        source_type="security_policy",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=2,
        confidence=0.8
    )
    
    evidence = [Evidence(claim=valid_claim)]
    violations = [Evidence(claim=violation_claim)]
    required = ["security_policy"]
    
    decision = evaluate(evidence, required, [], [], violations)
    
    assert decision.decision == "ESCALATE"
    assert "Permission Rule" in decision.rules_fired
