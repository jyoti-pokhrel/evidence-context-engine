# Evidence Context Engine

A context layer that determines whether an AI agent has sufficient trusted evidence to complete a software engineering task autonomously.

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-26%2F26%20passing-brightgreen.svg)

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup & Run
```bash
# Install dependencies
uv sync

# Run demo (4 scenarios)
uv run python demo.py

# Run test suite (26 tests)
uv run pytest tests/ -v
```

**What to expect:**
- 4 demo scenarios demonstrating different failure modes
- 26/26 tests passing
- Decision Brief output for each scenario

## Problem & Solution

**Problem:** Autonomous AI agents fail when reasoning over raw retrieved context. They cannot determine whether retrieved information is sufficient, fresh, authorized, or consistent. This leads to:
- **False confidence**: Proceeding with incomplete/conflicting context
- **Unnecessary escalation**: Blocking on tasks where sufficient evidence exists

**Solution:** A context layer that sits between data sources and the agent. It retrieves candidate context, validates evidence (freshness, permissions, conflicts), compresses validated evidence into a Decision Brief, and provides only the Decision Brief to the agent—not raw documents.

**Core Thesis:** Agents should reason over validated evidence—not raw retrieved context.

## Architecture Overview

```mermaid
flowchart TD
    Task["Task"] --> Planner["Context Planner"]
    Planner --> Retriever["Retriever<br/>(BM25)"]
    Retriever --> Engine["Context Engine<br/>(HERO)"]
    
    subgraph EngineBox["Context Engine Responsibilities"]
        E1["• Extract claims"]
        E2["• Validate freshness"]
        E3["• Check permissions"]
        E4["• Detect & resolve conflicts"]
        E5["• Extract facts"]
        E6["• Compress evidence"]
    end
    
    Engine --- EngineBox
    Engine --> WM[("Working Memory")]
    Engine --> Policy["Decision Policy"]
    Policy --> Brief["Decision Brief<br/>(ARTIFACT)"]
    
    style Engine fill:#e3f2fd,stroke:#1976d2,stroke-width:4px
    style EngineBox fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px
    style Brief fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style WM fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Components:**
- **Context Planner**: Determines required context categories
- **Retriever**: BM25-based document retrieval
- **Context Engine** (Hero): Validates freshness, checks permissions, detects/resolves conflicts, extracts facts, compresses context
- **Working Memory**: Task-scoped fact storage
- **Decision Policy**: Explicit rules (no ML) for PROCEED/ESCALATE
- **Decision Brief**: Final artifact with validated evidence

## Context Engineering Principles

**Select**: The Retriever uses BM25 to match documents to required context categories. Only relevant documents are passed forward.

**Write**: Working Memory stores facts discovered during claim extraction. Facts are key-value pairs with source attribution, task-scoped and reset between tasks.

**Compress**: Raw documents → Claims → Validated Evidence → Decision Brief. The brief contains only what's retained, not what's rejected.

**Isolate**: Only the Decision Brief is passed to downstream agents. Raw documents, retrieval results, and validation reasoning are excluded.

## How It Works

### Decision Flow

**PROCEED when:**
- All required context categories have validated claims
- No unresolved conflicts
- All claims are fresh enough
- No permission violations

**ESCALATE when:**
- Missing required context
- Unresolved conflicts (equal authority)
- Stale evidence for required context
- Permission violations for required context

### Conflict Resolution

When conflicts exist, resolution uses authority levels:
1. Code (highest)
2. Security Policy
3. Architecture Docs
4. README
5. Meeting Notes (lowest)

Conflicts between equal-authority sources are unresolvable and require human review.

### Failure Modes

| Failure Mode | Mitigation |
|--------------|------------|
| Context Poisoning | Freshness validation rejects stale docs |
| Context Clash | Authority-based conflict resolution |
| Context Distraction | Retrieval + claim extraction reduces noise |
| Context Confusion | Priority rules + explicit policy |

## Demo Scenarios

All scenarios use the same task: "Add rate limiting to the /login endpoint"

### Scenario 1: All Evidence Present → PROCEED

**Input:** `fixtures/scenario1/task.json`
```json
{
  "metadata": {
    "task_id": "task-001",
    "task_type": "rate_limiting",
    "description": "Add rate limiting to the /login endpoint"
  }
}
```

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "PROCEED",
  "reason": "All required evidence validated",
  "evidence_count": 49,
  "rules_fired": ["Proceed Rule"],
  "context_reduction": 0.117
}
```

### Scenario 2: Stale Architecture Doc → ESCALATE

**Input:** Architecture doc dated 2024-06-15 (>12 months old)

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Stale documentation for required context",
  "stale_count": 4,
  "rules_fired": ["Freshness Rule"]
}
```

### Scenario 3: Restricted Security Policy → ESCALATE

**Input:** `permissions.json` marks `security_policy.md` as restricted

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Insufficient authorized evidence",
  "permission_violations": 5,
  "missing": ["configuration"],
  "rules_fired": ["Permission Rule"]
}
```

### Scenario 4: Conflicting Claims → ESCALATE

**Input:** Two architecture docs (v2.0 and v2.1) disagree on auth method

**Output:** Decision Brief (trimmed)
```json
{
  "decision": "ESCALATE",
  "reason": "Unresolved conflicting evidence",
  "conflicts": 6,
  "rules_fired": ["Conflict Rule"]
}
```

## Validation

### Test Results

**Test Suite:** 26/26 tests passing

```bash
$ uv run pytest tests/ -v
============================= test session starts ==============================
tests/test_engine.py::test_extract_claims_from_document PASSED           [  3%]
tests/test_engine.py::test_validate_freshness_valid PASSED               [  7%]
...
tests/test_scenarios.py::test_scenario_1_proceeds PASSED                 [ 88%]
tests/test_scenarios.py::test_scenario_2_escalates_on_staleness PASSED   [ 92%]
tests/test_scenarios.py::test_scenario_3_escalates_on_permissions PASSED [ 96%]
tests/test_scenarios.py::test_scenario_4_escalates_on_conflict PASSED    [100%]
============================== 26 passed in 0.13s ==============================
```

### Evaluation Metrics

| Metric | Goal | Actual | Status |
|--------|------|--------|--------|
| Decision Accuracy | 4/4 scenarios correct | 4/4 | ✅ Pass |
| False Proceed Rate | 0% | 0% | ✅ Pass |
| False Escalation Rate | 0% | 0% | ✅ Pass |
| Context Reduction | >80% | 11.7% / 33.0% / 26.8% / 4.3% | ⚠️ Below target |
| Explainability | 100% | 100% | ✅ Pass |

**Detailed validation checklist:** See [`docs/VALIDATION.md`](docs/VALIDATION.md)

## Assumptions

- Repository size is small (<50 documents)
- Documents have timestamps (or timestamps can be inferred)
- Permissions are predefined in `permissions.json`
- One task per execution
- BM25 retrieval is sufficient for small corpus
- Conflict resolution by authority is acceptable (no ML needed)
- Claim extraction uses heuristic approach (no LLM required)

## Limitations

- One task per execution
- Working Memory resets between tasks
- BM25 retrieval (not suitable for large corpora)
- Context requirements are predefined
- Decision Brief is not consumed by an actual agent
- Context reduction metric below 80% target (see VALIDATION.md for explanation)

## Future Improvements

- Multi-agent integration (pass Decision Brief to actual agent)
- Persistent organizational memory (accumulate facts across tasks)
- Dynamic planning with LLMs (instead of rule-based context planning)
- Production retrieval pipeline (embeddings, vector search)
- Real-time updates as documents change
- LLM-based claim extraction (when API key is available)

## Documentation

- **[SPEC.md](docs/SPEC.md)**: Complete specification with all requirements
- **[AI_WORKFLOW.md](docs/AI_WORKFLOW.md)**: Multi-agent development workflow
- **[VALIDATION.md](docs/VALIDATION.md)**: Test results and metrics

## Project Structure

```
context-engine/
├── README.md
├── pyproject.toml
├── demo.py
├── docs/
│   ├── SPEC.md
│   ├── AI_WORKFLOW.md
│   └── VALIDATION.md
├── fixtures/
│   ├── scenario1/
│   ├── scenario2/
│   ├── scenario3/
│   └── scenario4/
├── context_engine/
│   ├── planner.py
│   ├── retriever.py
│   ├── engine.py
│   ├── working_memory.py
│   ├── policy.py
│   ├── brief.py
│   ├── loader.py
│   └── pipeline.py
├── schemas/
│   ├── task.py
│   ├── evidence.py
│   ├── working_memory.py
│   └── decision_brief.py
└── tests/
    ├── test_planner.py
    ├── test_retriever.py
    ├── test_engine.py
    ├── test_policy.py
    └── test_scenarios.py
```

## License

MIT
