# Validation Checklist

This document maps each specification success criterion to its verification method and current status.

## Specification Success Criteria

From `docs/SPEC.md` Section 15: Evaluation

| Criterion | Goal | Verification Method | Status | Measured Value |
|-----------|------|---------------------|--------|----------------|
| **Decision Accuracy** | System correctly identifies PROCEED vs ESCALATE for all 4 scenarios | `tests/test_scenarios.py` (test_scenario_1_proceeds, test_scenario_2_escalates_on_staleness, test_scenario_3_escalates_on_permissions, test_scenario_4_escalates_on_conflict) | ✅ Pass | 4/4 scenarios correct |
| **False Proceed Rate** | 0% (unsafe tasks should never proceed) | Scenarios 2-4 all correctly escalate | ✅ Pass | 0% (0/3 unsafe tasks proceeded) |
| **False Escalation Rate** | 0% (safe tasks should never escalate unnecessarily) | Scenario 1 correctly proceeds | ✅ Pass | 0% (0/1 safe task escalated) |
| **Context Reduction** | >80% (Decision Brief should be significantly smaller than raw docs) | Measured via `brief.context_reduction` field in Decision Brief | ⚠️ Below target | 11.7% / 33.0% / 26.8% / 4.3% (see explanation below) |
| **Explainability** | 100% (every decision includes `rules_fired` and explicit reasoning) | Every `PolicyDecision` includes `rules_fired`; enforced by `policy.py` always appending a rule | ✅ Pass | 100% (all 4 scenarios include rules_fired) |

## Sample Inputs and Outputs

All scenarios use the same task definition:

**Task Input** (`fixtures/scenario*/task.json`):
```json
{
  "metadata": {
    "task_id": "task-001",
    "task_type": "rate_limiting",
    "description": "Add rate limiting to the /login endpoint",
    "endpoint": "/login",
    "acceptance_criteria": [
      "Implement rate limiting middleware",
      "Apply to /login endpoint",
      "Configure rate limit parameters"
    ]
  }
}
```

The system requires 5 context categories: `endpoint_implementation`, `middleware`, `api_documentation`, `security_policy`, `configuration`.

---

### Scenario 1: All Evidence Present → PROCEED

**What makes this scenario work:**
- All required documents are present and fresh (dated within thresholds)
- No permission restrictions
- No conflicts between documents

**Input Files:**

`fixtures/scenario1/permissions.json`:
```json
{
  "access_control": {
    "agent_role": "developer",
    "allowed_documents": ["readme.md", "architecture.md", "api.md", "meeting_notes.md"],
    "restricted_documents": []
  }
}
```

`fixtures/scenario1/docs/`:
- `readme.md` (dated 2026-01-10) - mentions JWT authentication
- `architecture.md` (dated 2026-01-12) - describes JWT authentication, middleware chain, rate limiting config
- `api.md` (dated 2026-01-11) - documents /login endpoint, JWT tokens, rate limiting config
- `meeting_notes.md` (dated 2026-01-08) - discusses rate limiting implementation, JWT authentication

`fixtures/scenario1/repo/`:
- `login.py` (code) - /login endpoint implementation
- `middleware.py` (code) - auth and logging middleware
- `config.py` (code) - rate limiting configuration

**Output:** Decision Brief (representative sample)
```json
{
  "decision": "PROCEED",
  "reason": "All required evidence validated",
  "evidence": [
    {
      "claim": {
        "claim_id": "architecture.md_claim_8",
        "text": "The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.",
        "source": "architecture.md",
        "source_type": "architecture_docs",
        "topic": "authentication_method",
        "timestamp": "2026-01-12T00:00:00",
        "authority": 3,
        "confidence": 0.8,
        "is_fact": true,
        "fact_key": "auth_mechanism"
      },
      "validated_at": "2026-08-01T15:16:04.267531",
      "is_valid": true
    },
    {
      "claim": {
        "claim_id": "config.py_claim_4",
        "text": "RATE_LIMITING_REQUESTS_PER_MINUTE = 60",
        "source": "config.py",
        "source_type": "code",
        "topic": "rate_limiting",
        "timestamp": "2026-08-01T13:00:49.667010",
        "authority": 1,
        "confidence": 0.8,
        "is_fact": false,
        "fact_key": null
      },
      "validated_at": "2026-08-01T15:16:04.267758",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": [
      {
        "key": "auth_mechanism",
        "value": "Confirmed that we're using JWT tokens for authentication. The middleware validates the token on each request.",
        "source": "meeting_notes.md",
        "discovered_at": "2026-08-01 15:30:00.836128"
      },
      {
        "key": "auth_mechanism",
        "value": "The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.",
        "source": "architecture.md",
        "discovered_at": "2026-08-01 15:30:00.836157"
      },
      {
        "key": "auth_mechanism",
        "value": "2. Authentication middleware (JWT validation)",
        "source": "architecture.md",
        "discovered_at": "2026-08-01 15:30:00.836174"
      },
      {
        "key": "auth_mechanism",
        "value": "The application uses JWT tokens for authentication. Users must provide a valid JWT token in the Authorization header.",
        "source": "readme.md",
        "discovered_at": "2026-08-01 15:30:00.836243"
      },
      {
        "key": "auth_mechanism",
        "value": "\"\"\"Authentication middleware using JWT.\"\"\"",
        "source": "middleware.py",
        "discovered_at": "2026-08-01 15:30:00.836268"
      }
    ]
  },
  "missing": [],
  "conflicts": [],
  "stale": [],
  "permission_violations": [],
  "rules_fired": ["Proceed Rule"],
  "context_reduction": 0.117
}
```

**Summary:** 49 validated evidence items, 0 missing, 0 conflicts, 0 stale, 0 permission violations.

---

### Scenario 2: Stale Architecture Doc → ESCALATE

**What makes this scenario fail:**
- `architecture.md` is dated 2024-06-15 (>12 months old, threshold is 365 days)
- Architecture docs contain critical authentication and middleware information
- Stale architecture docs cause escalation via Freshness Rule

**Input Files:**

`fixtures/scenario2/permissions.json`:
```json
{
  "access_control": {
    "agent_role": "developer",
    "allowed_documents": ["readme.md", "architecture.md", "api.md", "meeting_notes.md"],
    "restricted_documents": []
  }
}
```

`fixtures/scenario2/docs/architecture.md` (THE KEY DIFFERENCE):
```markdown
# Architecture Documentation

## System Overview

The Evidence Context Engine is a FastAPI application.

### Authentication

The system uses basic session-based authentication. Users log in and receive a session cookie.

### Middleware

The application uses logging middleware only.

Last updated: 2024-06-15
```

**Output:** Decision Brief (representative sample)
```json
{
  "decision": "ESCALATE",
  "reason": "Stale documentation for required context",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint to prevent brute force attacks.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8,
        "is_fact": true
      },
      "validated_at": "2026-08-01T15:16:04.267492",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": []
  },
  "missing": [],
  "conflicts": [],
  "stale": [
    {
      "claim": {
        "claim_id": "architecture.md_claim_4",
        "text": "The Evidence Context Engine is a FastAPI application.",
        "source": "architecture.md",
        "source_type": "architecture_docs",
        "topic": "api_structure",
        "timestamp": "2024-06-15T00:00:00",
        "authority": 3,
        "confidence": 0.8,
        "is_fact": true
      },
      "validated_at": "2026-08-01T15:16:04.267528",
      "is_valid": false,
      "validation_reason": "Claim is 577 days old, threshold is 365 days"
    }
  ],
  "permission_violations": [],
  "rules_fired": ["Freshness Rule"],
  "context_reduction": 0.330
}
```

**Summary:** 27 validated evidence items, 4 stale claims from architecture.md (all rejected due to age).

---

### Scenario 3: Restricted Security Policy → ESCALATE

**What makes this scenario fail:**
- `security_policy.md` contains critical rate limiting requirements
- `security_policy.md` is marked as restricted in permissions.json
- Restricted documents cannot be used, causing escalation via Permission Rule

**Input Files:**

`fixtures/scenario3/permissions.json` (THE KEY DIFFERENCE):
```json
{
  "access_control": {
    "agent_role": "developer",
    "allowed_documents": ["readme.md", "architecture.md", "api.md", "meeting_notes.md"],
    "restricted_documents": ["security_policy.md"]
  }
}
```

`fixtures/scenario3/docs/security_policy.md` (RESTRICTED):
```markdown
# Security Policy

## Rate Limiting Requirements

All authentication endpoints must implement rate limiting to prevent brute force attacks.

**Requirements:**
- Maximum 5 failed login attempts per minute per IP
- Lock account after 10 failed attempts
- Log all rate limit violations

## Authentication Security

JWT tokens must:
- Expire after 1 hour
- Use RS256 algorithm
- Include user ID and role in claims

## Compliance

This policy is restricted to security team members only.

Last updated: 2026-01-09
```

**Output:** Decision Brief (representative sample)
```json
{
  "decision": "ESCALATE",
  "reason": "Insufficient authorized evidence",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint to prevent brute force attacks.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8,
        "is_fact": true
      },
      "validated_at": "2026-08-01T15:16:04.267492",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": [
      {
        "key": "auth_mechanism",
        "value": "The system uses OAuth2 with JWT tokens for authentication.",
        "source": "architecture.md",
        "discovered_at": "2026-08-01 15:32:07.788275"
      },
      {
        "key": "auth_mechanism",
        "value": "\"\"\"Authentication middleware using JWT.\"\"\"",
        "source": "middleware.py",
        "discovered_at": "2026-08-01 15:32:07.788299"
      },
      {
        "key": "auth_mechanism",
        "value": "The application uses JWT tokens for authentication.",
        "source": "readme.md",
        "discovered_at": "2026-08-01 15:32:07.788375"
      }
    ]
  },
  "missing": ["configuration"],
  "conflicts": [],
  "stale": [],
  "permission_violations": [
    {
      "claim": {
        "claim_id": "security_policy.md_claim_5",
        "text": "All authentication endpoints must implement rate limiting to prevent brute force attacks.",
        "source": "security_policy.md",
        "source_type": "security_policy",
        "topic": "rate_limiting",
        "timestamp": "2026-01-09T00:00:00",
        "authority": 2,
        "confidence": 0.8,
        "is_fact": true
      },
      "validated_at": "2026-08-01T15:16:04.267649",
      "is_valid": false,
      "validation_reason": "Document security_policy.md is restricted"
    }
  ],
  "rules_fired": ["Permission Rule"],
  "context_reduction": 0.268
}
```

**Summary:** 28 validated evidence items, 5 permission violations from security_policy.md (all rejected due to access control).

---

### Scenario 4: Conflicting Claims → ESCALATE

**What makes this scenario fail:**
- Two architecture docs (v2.0 and v2.1) disagree on authentication method
- `architecture_v2.0.md` says "JWT tokens" (dated 2025-12-15)
- `architecture_v2.1.md` says "OAuth2" (dated 2026-01-10)
- Both have same authority level (3), so conflict is unresolvable
- Unresolvable conflicts cause escalation via Conflict Rule

**Input Files:**

`fixtures/scenario4/permissions.json`:
```json
{
  "access_control": {
    "agent_role": "developer",
    "allowed_documents": ["readme.md", "architecture_v2.0.md", "architecture_v2.1.md", "api.md", "meeting_notes.md"],
    "restricted_documents": []
  }
}
```

`fixtures/scenario4/docs/architecture_v2.0.md` (THE KEY DIFFERENCE):
```markdown
# Architecture Documentation v2.0

## System Overview

The Evidence Context Engine is a FastAPI application.

### Authentication

The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.

### Middleware

The application uses logging and authentication middleware.

Last updated: 2025-12-15
```

`fixtures/scenario4/docs/architecture_v2.1.md` (THE KEY DIFFERENCE):
```markdown
# Architecture Documentation v2.1

## System Overview

The Evidence Context Engine is a FastAPI application.

### Authentication

The system uses OAuth2 for authentication. The /login endpoint validates credentials using OAuth2 flow and returns an access token.

### Middleware

The application uses logging and authentication middleware.

Last updated: 2026-01-10
```

**Output:** Decision Brief (representative sample)
```json
{
  "decision": "ESCALATE",
  "reason": "Unresolved conflicting evidence",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint to prevent brute force attacks.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8,
        "is_fact": true
      },
      "validated_at": "2026-08-01T15:16:04.267492",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": [
      {
        "key": "auth_mechanism",
        "value": "The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.",
        "source": "architecture_v2.0.md",
        "discovered_at": "2026-08-01 15:33:16.513023"
      },
      {
        "key": "auth_mechanism",
        "value": "The system uses OAuth2 for authentication. The /login endpoint validates credentials using OAuth2 flow and returns an access token.",
        "source": "architecture_v2.1.md",
        "discovered_at": "2026-08-01 15:33:16.513038"
      },
      {
        "key": "auth_mechanism",
        "value": "\"\"\"Authentication middleware using JWT.\"\"\"",
        "source": "middleware.py",
        "discovered_at": "2026-08-01 15:33:16.513052"
      },
      {
        "key": "auth_mechanism",
        "value": "The application uses JWT tokens for authentication.",
        "source": "readme.md",
        "discovered_at": "2026-08-01 15:33:16.513105"
      }
    ]
  },
  "missing": [],
  "conflicts": [
    {
      "claim_a": {
        "claim": {
          "claim_id": "architecture_v2.0.md_claim_8",
          "text": "The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.",
          "source": "architecture_v2.0.md",
          "source_type": "architecture_docs",
          "topic": "authentication_method",
          "timestamp": "2025-12-15T00:00:00",
          "authority": 3,
          "confidence": 0.8,
          "is_fact": true,
          "fact_key": "auth_mechanism"
        },
        "validated_at": "2026-08-01T15:16:04.267531",
        "is_valid": true
      },
      "claim_b": {
        "claim": {
          "claim_id": "architecture_v2.1.md_claim_8",
          "text": "The system uses OAuth2 for authentication. The /login endpoint validates credentials using OAuth2 flow and returns an access token.",
          "source": "architecture_v2.1.md",
          "source_type": "architecture_docs",
          "topic": "authentication_method",
          "timestamp": "2026-01-10T00:00:00",
          "authority": 3,
          "confidence": 0.8,
          "is_fact": true,
          "fact_key": "auth_mechanism"
        },
        "validated_at": "2026-08-01T15:16:04.267534",
        "is_valid": true
      },
      "topic": "authentication_method",
      "resolved": false,
      "winner": null,
      "resolution_reason": null
    }
  ],
  "stale": [],
  "permission_violations": [],
  "rules_fired": ["Conflict Rule"],
  "context_reduction": 0.043
}
```

**Summary:** 30 validated evidence items, 6 conflicts (all unresolvable due to equal authority level).

## Test Suite Results

All 26 tests pass:

```bash
$ uv run pytest tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/jyoti/Documents/code/projects/Evidence_Context_Engine
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 26 items

tests/test_engine.py::test_extract_claims_from_document PASSED           [  3%]
tests/test_engine.py::test_validate_freshness_valid PASSED               [  7%]
tests/test_engine.py::test_validate_freshness_stale PASSED               [ 11%]
tests/test_engine.py::test_check_permission_allowed PASSED               [ 15%]
tests/test_engine.py::test_check_permission_restricted PASSED            [ 19%]
tests/test_engine.py::test_detect_conflicts PASSED                       [ 23%]
tests/test_engine.py::test_resolve_conflict_higher_authority PASSED      [ 26%]
tests/test_engine.py::test_resolve_conflict_equal_authority PASSED       [ 30%]
tests/test_engine.py::test_process_documents PASSED                      [ 34%]
tests/test_planner.py::test_plan_context_rate_limiting PASSED            [ 38%]
tests/test_planner.py::test_plan_context_unknown_type PASSED             [ 42%]
tests/test_policy.py::test_evaluate_proceed PASSED                       [ 46%]
tests/test_policy.py::test_evaluate_missing_evidence PASSED              [ 50%]
tests/test_policy.py::test_evaluate_unresolved_conflicts PASSED          [ 54%]
tests/test_policy.py::test_evaluate_stale_evidence PASSED                [ 57%]
tests/test_policy.py::test_evaluate_permission_violations PASSED         [ 61%]
tests/test_retriever.py::test_retrieve_basic PASSED                      [ 65%]
tests/test_retriever.py::test_retrieve_empty_documents PASSED            [ 69%]
tests/test_scenarios.py::test_load_scenario_1 PASSED                     [ 73%]
tests/test_scenarios.py::test_load_scenario_2 PASSED                     [ 76%]
tests/test_scenarios.py::test_load_scenario_3 PASSED                     [ 80%]
tests/test_scenarios.py::test_load_scenario_4 PASSED                     [ 84%]
tests/test_scenarios.py::test_scenario_1_proceeds PASSED                 [ 88%]
tests/test_scenarios.py::test_scenario_2_escalates_on_staleness PASSED   [ 92%]
tests/test_scenarios.py::test_scenario_3_escalates_on_permissions PASSED [ 96%]
tests/test_scenarios.py::test_scenario_4_escalates_on_conflict PASSED    [100%]

============================== 26 passed in 0.18s ==============================
```

## Structured Validation Checklist

### Decision Accuracy
- [x] Scenario 1 (all evidence present) → PROCEED
- [x] Scenario 2 (stale architecture doc) → ESCALATE
- [x] Scenario 3 (restricted security policy) → ESCALATE
- [x] Scenario 4 (conflicting claims) → ESCALATE
- [x] All 4 scenarios produce correct decisions

### False Proceed Rate
- [x] Scenario 2 correctly escalates (stale docs)
- [x] Scenario 3 correctly escalates (permission violations)
- [x] Scenario 4 correctly escalates (conflicts)
- [x] 0% false proceed rate (0/3 unsafe tasks proceeded)

### False Escalation Rate
- [x] Scenario 1 correctly proceeds (all evidence present)
- [x] 0% false escalation rate (0/1 safe task escalated)

### Context Reduction
- [x] Metric defined in `context_engine/brief.py::_estimate_brief_size`
- [x] Only counts validated evidence and working memory facts
- [x] Does not count rejected items (stale, violations, conflicts, missing)
- [ ] Scenario 1: 11.7% reduction (below 80% target)
- [ ] Scenario 2: 33.0% reduction (below 80% target)
- [ ] Scenario 3: 26.8% reduction (below 80% target)
- [ ] Scenario 4: 4.3% reduction (below 80% target)
- [ ] See "Context Reduction Explanation" below for rationale

### Explainability
- [x] Every `PolicyDecision` includes `rules_fired` field
- [x] `policy.py` always appends a rule (Proceed Rule, Freshness Rule, etc.)
- [x] Scenario 1: `rules_fired = ["Proceed Rule"]`
- [x] Scenario 2: `rules_fired = ["Freshness Rule"]`
- [x] Scenario 3: `rules_fired = ["Permission Rule"]`
- [x] Scenario 4: `rules_fired = ["Conflict Rule"]`
- [x] 100% explainability (all 4 scenarios include rules_fired)

## Context Reduction Explanation

The context reduction metric measures how much the Decision Brief compresses the raw input documents. The target is >80% reduction, meaning the brief should be <20% of the raw doc size.

**Current results:**
- Scenario 1: 11.7% reduction (brief is 88.3% of raw size)
- Scenario 2: 33.0% reduction (brief is 67.0% of raw size)
- Scenario 3: 26.8% reduction (brief is 73.2% of raw size)
- Scenario 4: 4.3% reduction (brief is 95.7% of raw size)

**Why the target isn't met:**

The metric definition (in `context_engine/brief.py::_estimate_brief_size`) counts only validated evidence and working memory facts (what's retained), not diagnostic metadata like stale, violations, conflicts, or missing (what's rejected). This is the correct definition—a brief that correctly identifies and excludes stale claims should get credit for that exclusion, not be penalized by including their text length in the "compressed" size.

The low reduction is due to the **claim extraction heuristic** in `context_engine/engine.py::extract_claims_from_document`, which extracts any non-blank, non-heading line over 15 characters containing `.`, `=`, or `:` as a claim. This produces many claims (49 in scenario 1, 27 in scenario 2, etc.), making the brief large relative to the raw docs.

**Why we didn't tighten the extraction to hit the metric:**

Tightening the extraction heuristic to produce fewer claims would artificially improve the context reduction number, but it would be optimizing the wrong property. Fewer extracted claims isn't "better compression"—it's "less claim extraction," which is a different property. A system that extracts fewer claims might miss important evidence, leading to false escalations.

The current heuristic is intentionally permissive to avoid missing evidence. The tradeoff is documented in `README.md` under "Assumptions, Tradeoffs, Risks, and Privacy Boundaries → Tradeoffs → Heuristic vs. LLM-Based Claim Extraction."

**How a production system would improve this:**

A production system would use LLM-based claim extraction with structured output to extract only semantically meaningful claims, not every line that matches a pattern. This would dramatically reduce the number of claims (and thus the brief size) while improving claim quality. The LLM path is noted as future work in the README.

## Known Limitations (Not Affecting Validation)

These are spec deviations that don't affect the 4 demonstrated scenarios:

1. **Unknown task type fallback**: `planner.py` returns default categories instead of empty list for unknown task types (spec Section 8.0 says "return empty list (escalate)"). Not triggered by any demo scenario.

2. **Retriever low-relevance escalation**: `retriever.py` returns all documents sorted by score, even those with score 0 (spec Section 8.1 says "all documents have low relevance → return empty list"). Not triggered by any demo scenario.

3. **Claim extraction is heuristic, not LLM-based**: Spec Section 8.2 says "Extract claims from documents using LLM (structured output)." Implementation uses a heuristic line-splitting approach. Documented as intentional design choice in README.

These are documented in `README.md` under "Limitations" and `docs/AI_WORKFLOW.md` under "Examples of Catching AI Mistakes."
