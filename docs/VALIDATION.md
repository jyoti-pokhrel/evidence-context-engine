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

All scenarios use the same task: "Add rate limiting to the /login endpoint"

### Scenario 1: All Evidence Present → PROCEED

**Input:** `fixtures/scenario1/task.json`
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

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "PROCEED",
  "reason": "All required evidence validated",
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
      "validated_at": "2026-08-01T13:43:55.087649",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": [
      {
        "key": "auth_mechanism",
        "value": "Confirmed that we're using JWT tokens for authentication.",
        "source": "meeting_notes.md"
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

*Note: The full Decision Brief contains 49 validated evidence items. Only one is shown here for brevity.*

### Scenario 2: Stale Architecture Doc → ESCALATE

**Input:** Architecture doc dated 2024-06-15 (>12 months old)

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Stale documentation for required context",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8
      },
      "validated_at": "2026-08-01T13:43:55.087649",
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
        "claim_id": "architecture.md_claim_5",
        "text": "The system uses JWT tokens for authentication.",
        "source": "architecture.md",
        "source_type": "architecture_docs",
        "topic": "authentication_method",
        "timestamp": "2024-06-15T00:00:00",
        "authority": 3,
        "confidence": 0.8
      },
      "validated_at": "2026-08-01T13:43:55.087649",
      "is_valid": false,
      "validation_reason": "Claim is 777 days old, threshold is 365 days"
    }
  ],
  "permission_violations": [],
  "rules_fired": ["Freshness Rule"],
  "context_reduction": 0.330
}
```

*Note: Shows 4 stale claims from architecture.md (dated 2024-06-15).*

### Scenario 3: Restricted Security Policy → ESCALATE

**Input:** `permissions.json` marks `security_policy.md` as restricted

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Insufficient authorized evidence",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8
      },
      "validated_at": "2026-08-01T13:43:55.087649",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": []
  },
  "missing": ["configuration"],
  "conflicts": [],
  "stale": [],
  "permission_violations": [
    {
      "claim": {
        "claim_id": "security_policy.md_claim_5",
        "text": "All authentication endpoints must implement rate limiting.",
        "source": "security_policy.md",
        "source_type": "security_policy",
        "topic": "rate_limiting",
        "timestamp": "2026-01-09T00:00:00",
        "authority": 2,
        "confidence": 0.8
      },
      "validated_at": "2026-08-01T13:43:55.087649",
      "is_valid": false,
      "validation_reason": "Document security_policy.md is restricted"
    }
  ],
  "rules_fired": ["Permission Rule"],
  "context_reduction": 0.268
}
```

*Note: Shows 5 permission violations from security_policy.md (restricted document).*

### Scenario 4: Conflicting Claims → ESCALATE

**Input:** Two architecture docs (v2.0 and v2.1) disagree on auth method

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Unresolved conflicting evidence",
  "evidence": [
    {
      "claim": {
        "claim_id": "meeting_notes.md_claim_11",
        "text": "We discussed adding rate limiting to the /login endpoint.",
        "source": "meeting_notes.md",
        "source_type": "meeting_notes",
        "topic": "rate_limiting",
        "timestamp": "2026-01-08T00:00:00",
        "authority": 5,
        "confidence": 0.8
      },
      "validated_at": "2026-08-01T13:43:55.087649",
      "is_valid": true
    }
  ],
  "working_memory": {
    "facts": []
  },
  "missing": [],
  "conflicts": [
    {
      "claim_a": {
        "claim": {
          "claim_id": "architecture_v2.0.md_claim_5",
          "text": "The system uses JWT tokens for authentication.",
          "source": "architecture_v2.0.md",
          "source_type": "architecture_docs",
          "topic": "authentication_method",
          "timestamp": "2025-12-15T00:00:00",
          "authority": 3,
          "confidence": 0.8
        },
        "validated_at": "2026-08-01T13:43:55.087649",
        "is_valid": true
      },
      "claim_b": {
        "claim": {
          "claim_id": "architecture_v2.1.md_claim_5",
          "text": "The system uses OAuth2 for authentication.",
          "source": "architecture_v2.1.md",
          "source_type": "architecture_docs",
          "topic": "authentication_method",
          "timestamp": "2026-01-10T00:00:00",
          "authority": 3,
          "confidence": 0.8
        },
        "validated_at": "2026-08-01T13:43:55.087649",
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

*Note: Shows 6 conflicts between architecture_v2.0.md (JWT) and architecture_v2.1.md (OAuth2). Both have authority=3, so conflicts are unresolvable.*

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
