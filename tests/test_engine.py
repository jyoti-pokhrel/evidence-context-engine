from datetime import datetime
from context_engine.engine import (
    extract_claims_from_document,
    validate_freshness,
    check_permission,
    detect_conflicts,
    resolve_conflict,
    process_documents
)
from context_engine.retriever import Document
from context_engine.working_memory import WorkingMemory
from schemas.evidence import Claim


def test_extract_claims_from_document():
    doc = Document(
        doc_id="test.md",
        content="The system uses JWT tokens for authentication.\nThis is another line.",
        source_type="architecture_docs",
        timestamp="2026-01-10T00:00:00"
    )
    
    claims = extract_claims_from_document(doc)
    
    assert len(claims) > 0
    assert claims[0].source == "test.md"
    assert claims[0].source_type == "architecture_docs"


def test_validate_freshness_valid():
    claim = Claim(
        claim_id="test-1",
        text="Test claim",
        source="test.md",
        source_type="architecture_docs",
        topic="general",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    is_fresh, reason = validate_freshness(claim, datetime(2026, 1, 15))
    
    assert is_fresh is True
    assert reason is None


def test_validate_freshness_stale():
    claim = Claim(
        claim_id="test-1",
        text="Test claim",
        source="test.md",
        source_type="architecture_docs",
        topic="general",
        timestamp=datetime(2024, 1, 10),
        authority=3,
        confidence=0.8
    )
    
    is_fresh, reason = validate_freshness(claim, datetime(2026, 1, 15))
    
    assert is_fresh is False
    assert reason is not None


def test_check_permission_allowed():
    claim = Claim(
        claim_id="test-1",
        text="Test claim",
        source="readme.md",
        source_type="readme",
        topic="general",
        timestamp=datetime(2026, 1, 10),
        authority=4,
        confidence=0.8
    )
    
    has_permission, reason = check_permission(claim, ["readme.md"], [])
    
    assert has_permission is True
    assert reason is None


def test_check_permission_restricted():
    claim = Claim(
        claim_id="test-1",
        text="Test claim",
        source="security.md",
        source_type="security_policy",
        topic="general",
        timestamp=datetime(2026, 1, 10),
        authority=2,
        confidence=0.8
    )
    
    has_permission, reason = check_permission(claim, ["readme.md"], ["security.md"])
    
    assert has_permission is False
    assert reason is not None


def test_detect_conflicts():
    claim_a = Claim(
        claim_id="test-1",
        text="System uses JWT for authentication",
        source="doc1.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8,
        is_fact=True,
        fact_key="auth_mechanism",
        fact_value="JWT"
    )
    
    claim_b = Claim(
        claim_id="test-2",
        text="System uses OAuth for authentication",
        source="doc2.md",
        source_type="architecture_docs",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=3,
        confidence=0.8,
        is_fact=True,
        fact_key="auth_mechanism",
        fact_value="OAuth"
    )
    
    conflicts = detect_conflicts([claim_a, claim_b])
    
    assert len(conflicts) == 1


def test_resolve_conflict_higher_authority():
    claim_a = Claim(
        claim_id="test-1",
        text="Test A",
        source="doc1.md",
        source_type="code",
        topic="authentication_method",
        timestamp=datetime(2026, 1, 10),
        authority=1,
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
    
    winner, loser, reason = resolve_conflict(claim_a, claim_b)
    
    assert winner.claim_id == "test-1"
    assert reason == "Higher authority"


def test_resolve_conflict_equal_authority():
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
    
    winner, loser, reason = resolve_conflict(claim_a, claim_b)
    
    assert "Unresolvable" in reason


def test_process_documents():
    documents = [
        Document(
            doc_id="test.md",
            content="The system uses JWT tokens for authentication.",
            source_type="architecture_docs",
            timestamp="2026-01-10T00:00:00"
        )
    ]
    
    working_memory = WorkingMemory()
    validated, stale, violations, conflicts = process_documents(
        documents,
        working_memory,
        ["test.md"],
        [],
        datetime(2026, 1, 15)
    )
    
    assert len(validated) > 0
    assert len(stale) == 0
    assert len(violations) == 0
