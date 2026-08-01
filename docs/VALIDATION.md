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

## Additional Verification

### Demo Execution

All 4 scenarios can be executed via `uv run python demo.py` and produce the expected decisions:

```bash
$ uv run python demo.py
============================================================
EVIDENCE CONTEXT ENGINE - DEMO
============================================================

============================================================
SCENARIO 1
============================================================

Decision: PROCEED
Reason: All required evidence validated
Rules fired: ['Proceed Rule']
...

============================================================
SCENARIO 2
============================================================

Decision: ESCALATE
Reason: Stale documentation for required context
Rules fired: ['Freshness Rule']
...

============================================================
SCENARIO 3
============================================================

Decision: ESCALATE
Reason: Insufficient authorized evidence
Rules fired: ['Permission Rule']
...

============================================================
SCENARIO 4
============================================================

Decision: ESCALATE
Reason: Unresolved conflicting evidence
Rules fired: ['Conflict Rule']
...
```

### Test Suite

All 26 tests pass:

```bash
$ uv run pytest tests/ -v
============================= test session starts ==============================
...
tests/test_engine.py::test_extract_claims_from_document PASSED           [  3%]
tests/test_engine.py::test_validate_freshness_valid PASSED               [  7%]
...
tests/test_scenarios.py::test_scenario_1_proceeds PASSED                 [ 88%]
tests/test_scenarios.py::test_scenario_2_escalates_on_staleness PASSED   [ 92%]
tests/test_scenarios.py::test_scenario_3_escalates_on_permissions PASSED [ 96%]
tests/test_scenarios.py::test_scenario_4_escalates_on_conflict PASSED    [100%]

============================== 26 passed in 0.13s ==============================
```

## Known Limitations (Not Affecting Validation)

These are spec deviations that don't affect the 4 demonstrated scenarios:

1. **Unknown task type fallback**: `planner.py` returns default categories instead of empty list for unknown task types (spec Section 8.0 says "return empty list (escalate)"). Not triggered by any demo scenario.

2. **Retriever low-relevance escalation**: `retriever.py` returns all documents sorted by score, even those with score 0 (spec Section 8.1 says "all documents have low relevance → return empty list"). Not triggered by any demo scenario.

3. **Claim extraction is heuristic, not LLM-based**: Spec Section 8.2 says "Extract claims from documents using LLM (structured output)." Implementation uses a heuristic line-splitting approach. Documented as intentional design choice in README.

These are documented in `README.md` under "Limitations" and `docs/AI_WORKFLOW.md` under "Examples of Catching AI Mistakes."
