from datetime import datetime, timedelta
from typing import Optional
from schemas.evidence import Claim, Evidence, Conflict
from schemas.working_memory import WorkingMemory
from context_engine.retriever import Document


AUTHORITY_MAP = {
    "code": 1,
    "security_policy": 2,
    "architecture_docs": 3,
    "readme": 4,
    "meeting_notes": 5
}

FRESHNESS_THRESHOLDS = {
    "code": timedelta(days=365),
    "security_policy": timedelta(days=90),
    "architecture_docs": timedelta(days=365),
    "readme": timedelta(days=180),
    "meeting_notes": timedelta(days=180)
}


def extract_claims_from_document(document: Document) -> list[Claim]:
    claims = []
    content = document.content
    doc_id = document.doc_id
    source_type = document.source_type
    timestamp = datetime.fromisoformat(document.timestamp)
    authority = AUTHORITY_MAP.get(source_type, 5)
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if len(line) > 15 and ('.' in line or '=' in line or ':' in line):
            claim_id = f"{doc_id}_claim_{i}"
            topic = _infer_topic(line, source_type)
            
            claim = Claim(
                claim_id=claim_id,
                text=line,
                source=doc_id,
                source_type=source_type,
                topic=topic,
                timestamp=timestamp,
                authority=authority,
                confidence=0.8,
                is_fact=_is_fact(line),
                fact_key=_extract_fact_key(line, topic),
                fact_value=line
            )
            claims.append(claim)
    
    return claims


def _infer_topic(text: str, source_type: str) -> str:
    text_lower = text.lower()
    if 'authentication' in text_lower or 'jwt' in text_lower or 'oauth' in text_lower:
        return 'authentication_method'
    elif 'rate limit' in text_lower or 'rate_limit' in text_lower:
        return 'rate_limiting'
    elif 'middleware' in text_lower:
        return 'middleware'
    elif 'api' in text_lower or 'endpoint' in text_lower:
        return 'api_structure'
    elif 'config' in text_lower:
        return 'configuration'
    else:
        return 'general'


def _is_fact(text: str) -> bool:
    fact_indicators = ['uses', 'is', 'are', 'has', 'have', 'implements', 'requires']
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in fact_indicators)


def _extract_fact_key(text: str, topic: str) -> Optional[str]:
    if topic == 'authentication_method':
        if 'jwt' in text.lower():
            return 'auth_mechanism'
        elif 'oauth' in text.lower():
            return 'auth_mechanism'
    return None


def validate_freshness(claim: Claim, reference_date: Optional[datetime] = None) -> tuple[bool, Optional[str]]:
    if reference_date is None:
        reference_date = datetime.now()
    
    threshold = FRESHNESS_THRESHOLDS.get(claim.source_type, timedelta(days=180))
    age = reference_date - claim.timestamp
    
    if age > threshold:
        return False, f"Claim is {age.days} days old, threshold is {threshold.days} days"
    
    return True, None


def check_permission(claim: Claim, allowed_documents: list[str], restricted_documents: list[str]) -> tuple[bool, Optional[str]]:
    if claim.source in restricted_documents:
        return False, f"Document {claim.source} is restricted"
    
    if claim.source not in allowed_documents:
        return False, f"Document {claim.source} is not in allowed list"
    
    return True, None


def detect_conflicts(claims: list[Claim]) -> list[tuple[Claim, Claim]]:
    conflicts = []
    claims_by_topic = {}
    
    for claim in claims:
        if claim.topic not in claims_by_topic:
            claims_by_topic[claim.topic] = []
        claims_by_topic[claim.topic].append(claim)
    
    for topic, topic_claims in claims_by_topic.items():
        if len(topic_claims) < 2:
            continue
        
        for i in range(len(topic_claims)):
            for j in range(i + 1, len(topic_claims)):
                claim_a = topic_claims[i]
                claim_b = topic_claims[j]
                
                if _claims_conflict(claim_a, claim_b):
                    conflicts.append((claim_a, claim_b))
    
    return conflicts


def _claims_conflict(claim_a: Claim, claim_b: Claim) -> bool:
    if claim_a.fact_key != claim_b.fact_key:
        return False
    
    if claim_a.fact_key is None:
        return False
    
    if claim_a.fact_key != 'auth_mechanism':
        return False
    
    text_a = claim_a.text.lower()
    text_b = claim_b.text.lower()
    
    a_jwt_only = 'jwt' in text_a and 'oauth' not in text_a
    b_jwt_only = 'jwt' in text_b and 'oauth' not in text_b
    a_oauth_only = ('oauth' in text_a or 'oauth2' in text_a) and 'jwt' not in text_a
    b_oauth_only = ('oauth' in text_b or 'oauth2' in text_b) and 'jwt' not in text_b
    
    if (a_jwt_only and b_oauth_only) or (a_oauth_only and b_jwt_only):
        return True
    
    return False


def resolve_conflict(claim_a: Claim, claim_b: Claim) -> tuple[Claim, Claim, str]:
    if claim_a.authority < claim_b.authority:
        return claim_a, claim_b, "Higher authority"
    elif claim_b.authority < claim_a.authority:
        return claim_b, claim_a, "Higher authority"
    
    return claim_a, claim_b, "Unresolvable - equal authority"


def process_documents(
    documents: list[Document],
    working_memory: WorkingMemory,
    allowed_documents: list[str],
    restricted_documents: list[str],
    reference_date: Optional[datetime] = None
) -> tuple[list[Evidence], list[Evidence], list[Evidence], list[Conflict]]:
    all_claims = []
    for doc in documents:
        claims = extract_claims_from_document(doc)
        all_claims.extend(claims)
    
    validated_evidence = []
    stale_evidence = []
    permission_violations = []
    
    for claim in all_claims:
        is_fresh, freshness_reason = validate_freshness(claim, reference_date)
        if not is_fresh:
            stale_evidence.append(Evidence(
                claim=claim,
                is_valid=False,
                validation_reason=freshness_reason
            ))
            continue
        
        has_permission, permission_reason = check_permission(
            claim, allowed_documents, restricted_documents
        )
        if not has_permission:
            permission_violations.append(Evidence(
                claim=claim,
                is_valid=False,
                validation_reason=permission_reason
            ))
            continue
        
        validated_evidence.append(Evidence(
            claim=claim,
            is_valid=True
        ))
        
        if claim.is_fact and claim.fact_key:
            working_memory.add_fact(
                key=claim.fact_key,
                value=claim.fact_value,
                source=claim.source
            )
    
    conflicts_raw = detect_conflicts([e.claim for e in validated_evidence])
    conflicts = []
    
    for claim_a, claim_b in conflicts_raw:
        winner, loser, reason = resolve_conflict(claim_a, claim_b)
        
        if "Unresolvable" in reason:
            conflicts.append(Conflict(
                claim_a=Evidence(claim=claim_a),
                claim_b=Evidence(claim=claim_b),
                topic=claim_a.topic,
                resolved=False
            ))
        else:
            conflict = Conflict(
                claim_a=Evidence(claim=winner),
                claim_b=Evidence(claim=loser),
                topic=claim_a.topic,
                resolved=True,
                winner=Evidence(claim=winner),
                resolution_reason=reason
            )
            conflicts.append(conflict)
            
            validated_evidence = [e for e in validated_evidence if e.claim.claim_id != loser.claim_id]
    
    return validated_evidence, stale_evidence, permission_violations, conflicts
