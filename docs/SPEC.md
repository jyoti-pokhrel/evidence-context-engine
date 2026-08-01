# Evidence Context Engine — Specification

## 1. Problem Statement

Autonomous AI agents fail when reasoning over raw retrieved context because they lack mechanisms to evaluate context quality. Agents retrieve documents but cannot determine:

- Whether the retrieved context is **sufficient** to complete the task
- Whether the context is **fresh** enough to be trustworthy
- Whether the context contains **conflicts** that create ambiguity
- Whether the context is **authorized** for the agent to use

This leads to two failure modes:
1. **False confidence**: Agent proceeds with incomplete or conflicting context, producing incorrect implementations
2. **Unnecessary escalation**: Agent blocks on tasks where sufficient evidence exists but hasn't been validated

The goal is **not** to retrieve more information. The goal is to determine whether **sufficient trusted evidence** exists for autonomous action.

---

## 2. System Goal

> Evidence Context Engine transforms structured and unstructured organizational data into a trusted **Decision Brief** that determines whether an AI agent has sufficient validated evidence to act autonomously or should escalate.

The system produces a single artifact: the Decision Brief. This brief contains only validated evidence, explicit reasoning, and a clear decision (PROCEED or ESCALATE).

---

## 3. Core Thesis

> **Agents should reason over validated evidence—not raw retrieved context.**

The context layer sits between data sources and the agent. It does not pass raw documents to the agent. Instead, it:
1. Retrieves candidate context
2. Validates evidence (freshness, permissions, conflicts)
3. Compresses validated evidence into a Decision Brief
4. Provides the Decision Brief as the only context for the agent

This ensures the agent reasons over **trusted, compressed, authorized context**—not noisy, potentially stale, potentially conflicting raw documents.

---

## 4. Scope

### In Scope

- **One software engineering task**: "Add rate limiting to the /login endpoint"
- **One repository**: A small Python web application with ~10 files
- **Four demo scenarios**: Demonstrating different failure modes
- **Produce a Decision Brief**: The final artifact
- **Explicit decision policy**: Rule-based, auditable, deterministic
- **Context engineering principles**: Select, Write, Compress, Isolate

### Out of Scope

- **Code generation**: The system does not implement the rate limiting
- **Autonomous execution**: The system does not modify the repository
- **Maker/Checker agents**: The system stops at the Decision Brief
- **Multi-task support**: One task per execution
- **Persistent memory**: Working memory resets between tasks
- **Production retrieval pipeline**: Simplified BM25 retrieval for prototype

---

## 5. Users

| User | Role |
|------|------|
| **AI coding agent** | Consumes the Decision Brief to decide whether to proceed or escalate |
| **Human reviewer** | Reviews the Decision Brief to understand why the agent proceeded or escalated |
| **Engineering platform** | Integrates the context engine into CI/CD or development workflows |

---

## 6. Inputs

### Structured

- **Issue**: Task description, metadata, acceptance criteria
- **Repository metadata**: File tree, git history, dependencies
- **Permissions**: Access control list (who can access what)
- **Configuration**: App settings, environment variables

### Unstructured

- **README.md**: Project overview (may be stale)
- **Architecture docs**: System design (may be outdated)
- **API docs**: Endpoint specifications (may be incomplete)
- **Meeting notes**: Design decisions (may be informal)
- **Source code**: Implementation details (authoritative but may not reflect intent)

---

## 7. Output: Decision Brief

The Decision Brief is the **only artifact** produced by the system. It contains:

| Field | Type | Purpose |
|-------|------|---------|
| `decision` | `PROCEED \| ESCALATE` | Final decision |
| `reason` | `string \| null` | Why this decision was made |
| `evidence` | `list[Evidence]` | Validated claims supporting the decision |
| `working_memory` | `WorkingMemory` | Facts discovered during processing |
| `missing` | `list[str]` | Required context that was not found |
| `conflicts` | `list[Conflict]` | Conflicting claims (if any) |
| `stale` | `list[Evidence]` | Stale evidence that was rejected |
| `permission_violations` | `list[Evidence]` | Restricted evidence that was excluded |
| `rules_fired` | `list[str]` | Exact policy rules that triggered the decision |
| `context_reduction` | `float` | Ratio of raw docs to compressed brief |

**Why this structure?**
- `evidence`: Only validated claims, not raw documents
- `missing`: Explicit about what's absent
- `conflicts`: Shows unresolved ambiguity
- `rules_fired`: Makes the decision auditable and explainable
- `context_reduction`: Demonstrates compression effectiveness

---

## 8. Functional Requirements

### 8.0 Context Planner

**Inputs:**
- Task description and metadata

**Outputs:**
- Required context categories (e.g., `["endpoint_implementation", "middleware", "api_documentation", "security_policy", "configuration"]`)

**Responsibilities:**
- Determine what context categories are needed for the task
- Use rule-based mapping from task type to required categories
- Provide categories to Retriever for matching

**Failure Cases:**
- Unknown task type → return empty list (escalate)

---

### 8.1 Retriever

**Inputs:**
- Required context categories (from planner)
- Document corpus

**Outputs:**
- Ranked list of document IDs with relevance scores

**Responsibilities:**
- Match required context to available documents
- Use BM25 for lexical matching
- Return top-k candidates for validation

**Failure Cases:**
- No documents match required context → return empty list
- All documents have low relevance → return empty list (escalate)

---

### 8.2 Context Engine (Hero Component)

**Inputs:**
- Retrieved documents
- Working memory

**Outputs:**
- Validated evidence list
- Updated working memory

**Responsibilities:**
1. **Extract claims** from documents using LLM (structured output)
2. **Validate freshness** (reject stale claims)
3. **Check permissions** (exclude restricted claims)
4. **Detect conflicts** (identify contradictory claims by topic)
5. **Resolve conflicts** (using authority + freshness)
6. **Extract facts** (write to working memory)
7. **Compress** (return only validated evidence)

**Failure Cases:**
- No claims extracted → escalate (missing evidence)
- All claims stale → escalate (stale documentation)
- Unresolvable conflicts → escalate (conflicting evidence)
- Permission violations → escalate (insufficient authorized evidence)

---

### 8.3 Working Memory

**Inputs:**
- Facts extracted during processing

**Outputs:**
- Updated working memory state

**Responsibilities:**
- Store discovered facts (key-value pairs with source)
- Provide facts for decision brief
- Reset between tasks (task-scoped, not persistent)

**Failure Cases:**
- No facts extracted → empty working memory (acceptable)

---

### 8.4 Decision Policy

**Inputs:**
- Validated evidence list
- Required context categories
- Working memory

**Outputs:**
- Decision (PROCEED or ESCALATE)
- Reason
- Rules fired

**Responsibilities:**
- Check all required context exists
- Check no unresolved conflicts
- Check freshness thresholds met
- Check no permission violations
- Apply explicit rules (no ML)

**Failure Cases:**
- Missing required context → ESCALATE
- Unresolved conflicts → ESCALATE
- Stale evidence → ESCALATE
- Permission violations → ESCALATE

---

### 8.5 Decision Brief

**Inputs:**
- Decision
- Validated evidence
- Working memory
- Missing context
- Conflicts
- Stale evidence
- Permission violations
- Rules fired

**Outputs:**
- Structured Decision Brief (JSON)

**Responsibilities:**
- Assemble all fields into final artifact
- Calculate context reduction ratio
- Format for downstream consumption

**Failure Cases:**
- None (always produces a brief)

---

## 9. Architecture

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
   ├── Conflict Resolution (authority + freshness)
   ├── Fact Extraction (→ Working Memory)
   └── Compression
   │
   ▼
Decision Policy
   │
   ▼
Decision Brief (ARTIFACT)
```

---

## 10. Decision Policy

### Proceed When

All of the following are true:
1. ✓ All required context categories have at least one validated claim
2. ✓ No unresolved conflicts (all conflicts resolved by authority + freshness)
3. ✓ All claims are within freshness thresholds
4. ✓ No permission violations

### Escalate When

Any of the following are true:
1. ✗ Missing required context (one or more categories have no validated claims)
2. ✗ Unresolved conflicts (conflicting claims with equal authority)
3. ✗ Stale evidence (claims older than freshness thresholds)
4. ✗ Permission violations (restricted claims needed but not accessible)

### Rules (in priority order)

1. **Missing Evidence Rule**: If any required context category has no validated claims → ESCALATE
2. **Conflict Rule**: If conflicting claims exist and cannot be resolved → ESCALATE
3. **Freshness Rule**: If any required claim is stale → ESCALATE
4. **Permission Rule**: If any required claim is restricted → ESCALATE
5. **Proceed Rule**: If all checks pass → PROCEED

---

## 11. Context Engineering

### Select

**How relevant context is retrieved:**
- Context Planner determines required context categories
- Retriever uses BM25 to match documents to categories
- Top-k candidates passed to Context Engine for validation

### Write

**How facts are stored during execution:**
- Working Memory stores facts discovered during claim extraction
- Facts are key-value pairs with source attribution
- Working Memory is task-scoped (resets between tasks)
- Facts are included in Decision Brief for downstream use

### Compress

**How retrieved documents become a compact Decision Brief:**
- Raw documents → Claims (extraction via LLM)
- Claims → Validated Evidence (validation + conflict resolution)
- Validated Evidence + Working Memory → Decision Brief (compression)
- Context reduction ratio measures compression effectiveness

### Isolate

**Why only the Decision Brief is passed to downstream agents:**
- Decision Brief contains only validated evidence
- Raw documents, retrieval results, and validation reasoning are excluded
- Agent reasons over trusted, compressed context
- Prevents agent from reasoning over noisy, conflicting, or unauthorized data

---

## 12. Failure Modes

### Context Poisoning

**Problem:** Stale or outdated documents mislead the agent.

**Solution:** Freshness validation rejects claims older than thresholds. Stale evidence is excluded from Decision Brief and reported in `stale` field.

### Context Clash

**Problem:** Conflicting claims create ambiguity.

**Solution:** Conflict detection identifies contradictory claims. Conflicts resolved by authority + freshness. Unresolvable conflicts trigger escalation.

### Context Distraction

**Problem:** Irrelevant documents create noise.

**Solution:** Retrieval filters by relevance. Claim extraction focuses on task-relevant facts. Decision Brief includes only validated evidence.

### Context Confusion

**Problem:** Agent cannot determine which claims are authoritative.

**Solution:** Priority rules (authority + freshness) resolve conflicts. Decision Brief includes `rules_fired` for explainability.

---

## 13. Assumptions

- Repository size is small (<50 documents)
- Documents have timestamps (or timestamps can be inferred)
- Permissions are predefined in a configuration file
- One task per execution
- Claims are extracted dynamically from documents using an LLM
- BM25 retrieval is sufficient for small corpus
- Conflict resolution by authority + freshness is acceptable
- Conflicts between equal-authority sources are unresolvable (require human review)

---

## 14. Limitations

**What this prototype does not solve:**

- **Multi-task support**: Only one task per execution
- **Persistent memory**: Working memory resets between tasks
- **Production retrieval**: BM25 is not suitable for large corpora
- **Dynamic planning**: Context requirements are predefined
- **Agent integration**: Decision Brief is not actually consumed by an agent
- **Real-time updates**: No mechanism for updating claims as documents change
- **Multi-agent coordination**: No support for multiple agents with different context needs

---

## 15. Evaluation

### Metrics

| Metric | Goal |
|--------|------|
| **Decision Accuracy** | System correctly identifies PROCEED vs ESCALATE for all 4 scenarios |
| **False Proceed Rate** | 0% (unsafe tasks should never proceed) |
| **False Escalation Rate** | 0% (safe tasks should never escalate unnecessarily) |
| **Context Reduction** | >80% (Decision Brief should be significantly smaller than raw docs) |
| **Explainability** | 100% (every decision includes `rules_fired` and explicit reasoning) |

### Success Criteria

- All 4 demo scenarios produce correct decisions
- Decision Brief is auditable (includes all required fields)
- Context Engine demonstrates all four principles (Select, Write, Compress, Isolate)
- System is deterministic and reproducible

---

## 16. Demo Scenarios

### Scenario 1: All Evidence Present

**Input:**
- Task: "Add rate limiting to /login"
- All required documents present and fresh
- No conflicts
- No permission restrictions

**Expected Decision:** PROCEED

**Expected Decision Brief:**
- `decision`: PROCEED
- `evidence`: 5+ validated claims
- `missing`: []
- `conflicts`: []
- `stale`: []
- `permission_violations`: []
- `rules_fired`: ["Proceed Rule"]

---

### Scenario 2: Stale Architecture Doc

**Input:**
- Task: "Add rate limiting to /login"
- Architecture doc is >12 months old
- All other documents fresh

**Expected Decision:** ESCALATE

**Expected Decision Brief:**
- `decision`: ESCALATE
- `reason`: "Stale documentation"
- `stale`: [architecture claim]
- `rules_fired`: ["Freshness Rule"]

---

### Scenario 3: Restricted Security Policy

**Input:**
- Task: "Add rate limiting to /login"
- Security policy is marked as restricted
- Agent does not have permission to access

**Expected Decision:** ESCALATE

**Expected Decision Brief:**
- `decision`: ESCALATE
- `reason`: "Insufficient authorized evidence"
- `missing`: ["security_policy"]
- `permission_violations`: [security claim]
- `rules_fired`: ["Permission Rule"]

---

### Scenario 4: Conflicting Claims

**Input:**
- Task: "Add rate limiting to /login"
- Architecture doc (v2.1, Jan 2026) says "Authentication uses OAuth2"
- Architecture doc (v2.0, Dec 2025) says "Authentication uses JWT"
- Both documents are fresh and accessible, same authority level

**Expected Decision:** ESCALATE

**Expected Decision Brief:**
- `decision`: ESCALATE
- `reason`: "Conflicting evidence"
- `conflicts`: [(OAuth2 claim, JWT claim)]
- `rules_fired`: ["Conflict Rule"]

**Note:** Conflicts between documents of equal authority cannot be resolved automatically, even if one is newer. Both are within freshness thresholds. Human review required.

---

## 17. Future Work

- **Multi-agent integration**: Pass Decision Brief to actual agent for code generation
- **Persistent organizational memory**: Accumulate facts across tasks with invalidation
- **Dynamic planning**: LLM-based context planning instead of rule-based
- **Production retrieval pipeline**: Embeddings, vector search, hybrid retrieval
- **Real-time updates**: Update claims as documents change
- **Multi-task support**: Process multiple tasks in parallel
- **Agent-specific context**: Different context needs for different agents

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **Decision Brief** | The final artifact containing validated evidence and decision |
| **Evidence** | A validated claim with metadata (source, timestamp, confidence) |
| **Claim** | A fact extracted from a document |
| **Working Memory** | Task-scoped storage for discovered facts |
| **Context Engine** | Hero component that validates, resolves conflicts, and compresses context |
| **Context Reduction** | Ratio of raw document size to Decision Brief size |

---

## Appendix: Design Decisions

| Decision | Rationale |
|----------|-----------|
| BM25 only (no embeddings) | Sufficient for <20 docs, minimal dependencies |
| Dynamic claim extraction | Demonstrates evidence extraction from raw documents |
| Authority + freshness for conflicts | More nuanced than document type alone |
| Working Memory (not long-term) | Task-scoped, deterministic, reproducible |
| Stop at Decision Brief | Focus on context layer, not agent implementation |
| Explicit policy rules | Auditable, deterministic, explainable |

---

**Specification Version:** 1.1  
**Last Updated:** 2026-01-12  
**Status:** Reviewed — Ready for Implementation Plan
