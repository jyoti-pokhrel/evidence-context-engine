# Evidence Context Engine

A context layer that determines whether an AI agent has sufficient trusted evidence to complete a software engineering task autonomously.

## Core Thesis

> **Agents should reason over validated evidence—not raw retrieved context.**

The Evidence Context Engine sits between data sources and the agent. It does not pass raw documents to the agent. Instead, it retrieves candidate context, validates evidence (freshness, permissions, conflicts), compresses validated evidence into a Decision Brief, and provides the Decision Brief as the only context for the agent.

## Architecture

```
Task
   │
   ▼
Context Planner
   │
   ▼
Retriever (BM25)
   │
   ▼
Context Engine (HERO)
   │
   ├── Claim Extraction
   ├── Freshness Validation
   ├── Permission Checks
   ├── Conflict Detection
   ├── Conflict Resolution (authority)
   ├── Fact Extraction (→ Working Memory)
   └── Compression
   │
   ▼
Decision Policy
   │
   ▼
Decision Brief (ARTIFACT)
```

## Context Engineering Principles

### Select
The Retriever uses BM25 to match documents to required context categories determined by the Context Planner.

### Write
Working Memory stores facts discovered during claim extraction. Facts are key-value pairs with source attribution, task-scoped and reset between tasks.

### Compress
Raw documents become claims through extraction. Claims become validated evidence through validation and conflict resolution. Validated evidence becomes the Decision Brief through compression.

### Isolate
Only the Decision Brief is passed to downstream agents. Raw documents, retrieval results, and validation reasoning are excluded.

## Components

### Context Planner
Determines what context categories are needed for the task using rule-based mapping.

### Retriever
Uses BM25 for lexical matching to find relevant documents.

### Context Engine (Hero Component)
The core innovation. Validates freshness, checks permissions, detects and resolves conflicts, extracts facts, and compresses context.

### Working Memory
Task-scoped storage for discovered facts.

### Decision Policy
Applies explicit rules (no ML) to determine PROCEED or ESCALATE.

### Decision Brief
The final artifact containing validated evidence, decision, reasoning, and metadata.

## Decision Policy

### Proceed When
- All required context categories have validated claims
- No unresolved conflicts
- All claims are fresh enough
- No permission violations

### Escalate When
- Missing required context
- Unresolved conflicts (equal authority)
- Stale evidence for required context
- Permission violations for required context

## Context Priority

When conflicts exist, resolution uses authority levels:

1. Code (highest)
2. Security Policy
3. Architecture Docs
4. README
5. Meeting Notes (lowest)

Conflicts between equal-authority sources are unresolvable and require human review.

## Failure Modes

| Failure Mode | Mitigation |
|--------------|------------|
| Context Poisoning | Freshness validation rejects stale docs |
| Context Clash | Authority-based conflict resolution |
| Context Distraction | Retrieval + claim extraction reduces noise |
| Context Confusion | Priority rules + explicit policy |

## Demo Scenarios

### Scenario 1: All Evidence Present
**Decision:** PROCEED  
**Reason:** All required evidence validated

### Scenario 2: Stale Architecture Doc
**Decision:** ESCALATE  
**Reason:** Stale documentation for required context

### Scenario 3: Restricted Security Policy
**Decision:** ESCALATE  
**Reason:** Insufficient authorized evidence

### Scenario 4: Conflicting Claims
**Decision:** ESCALATE  
**Reason:** Unresolved conflicting evidence (equal authority)

## Installation

```bash
uv sync
```

## Usage

Run the demo:

```bash
uv run python demo.py
```

Run tests:

```bash
uv run pytest tests/ -v
```

## Stable vs Dynamic Context

### Stable Context
- System prompt
- Decision policy rules
- Tool definitions
- Priority order
- Freshness thresholds

### Dynamic Context
- Retrieved evidence
- Current task description
- Working Memory (discovered facts)
- Decision Brief
- Agent state

## Project Structure

```
context-engine/
├── README.md
├── pyproject.toml
├── demo.py
├── docs/
│   └── SPEC.md
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
│   └── loader.py
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

## Evaluation Metrics

| Metric | Goal |
|--------|------|
| Decision Accuracy | Correctly identifies PROCEED vs ESCALATE |
| False Proceed Rate | 0% (unsafe tasks never proceed) |
| False Escalation Rate | 0% (safe tasks never escalate unnecessarily) |
| Context Reduction | >80% (Decision Brief significantly smaller than raw docs) |
| Explainability | 100% (every decision includes rules_fired) |

## Limitations

- One task per execution
- Working Memory resets between tasks
- BM25 retrieval (not suitable for large corpora)
- Context requirements are predefined
- Decision Brief is not consumed by an actual agent

## Future Work

- Multi-agent integration
- Persistent organizational memory
- Dynamic planning with LLMs
- Production retrieval pipeline (embeddings, vector search)
- Real-time updates as documents change

## License

MIT
