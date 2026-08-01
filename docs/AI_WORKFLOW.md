# AI Development Workflow

This document describes the multi-agent workflow I used to develop the Evidence Context Engine, including the iterative refinement process and how different AI tools contributed to different phases.

## Workflow Overview

I used a multi-agent approach with clear separation of concerns:

- **Me**: Orchestrator, tester, solution proposer
- **ChatGPT + Claude**: Requirement refinement
- **opencode agent (qwen3.7-plus)**: Implementation planning and coding
- **Claude**: Code review against specification

The workflow was iterative, with multiple test-fix cycles and spec compliance reviews.

## Phase 1: Requirement Refinement

**Tools**: ChatGPT, Claude

I wrote the initial requirements document describing the Evidence Context Engine concept, scope, and expected behavior.

**ChatGPT's contribution**:
- Refined the problem statement
- Clarified the distinction between context retrieval and context validation
- Suggested focusing on a single concrete task (rate limiting) rather than general-purpose context management

**Claude's contribution**:
- Strengthened the failure mode analysis (context poisoning, clash, distraction, confusion)
- Proposed the Decision Brief as the core artifact
- Suggested explicit decision policy rules for auditability

**Outcome**: A refined requirements document that became the specification (`docs/SPEC.md`).

## Phase 2: Implementation Planning

**Tools**: opencode agent (qwen3.7-plus), Claude, Me

The opencode agent with qwen3.7-plus created the initial implementation plan based on the specification, including:
- Project structure
- Component responsibilities
- Data flow
- Testing strategy

**Claude's review of the plan**:
- Identified that the plan was too focused on retrieval, not context engineering
- Suggested making the Context Engine the "hero component" rather than the retriever

**My additions**:
After reviewing Claude's feedback, I added the four context engineering principles:
- **Select**: How relevant context is retrieved
- **Write**: How facts are stored during execution (Working Memory)
- **Compress**: How retrieved documents become a compact Decision Brief
- **Isolate**: Why only the Decision Brief is passed to downstream agents

These principles were integrated into the plan and became the architectural foundation.

**Outcome**: A solid implementation plan that balanced technical correctness with the context engineering thesis.

## Phase 3: Implementation and Testing

**Tools**: opencode agent (qwen3.7-plus), Me

qwen3.7-plus implemented the code based on the plan, producing:
- Core components (planner, retriever, engine, policy, brief)
- Schema definitions
- Fixture documents for 4 scenarios
- Initial test suite

**First test cycle**:
I ran the demo and tests, discovering two major issues:

1. **Decision accuracy problems**:
   - Scenario 1 (all evidence present) was producing ESCALATE instead of PROCEED
   - Scenario 3 (restricted security policy) was missing the permission violation
   - Root cause: The retriever wasn't returning all relevant documents, and the policy wasn't checking permission violations properly

2. **Context reduction metric was off**:
   - Initial value: ~11.7% (brief was 88.3% of raw doc size)
   - Target: >80% reduction (brief should be <20% of raw doc size)
   - Root cause: The metric was counting rejected items (stale, violations, conflicts) in the "compressed" size, which is backwards

**My proposed solutions**:
- Fix retriever to return all documents with non-zero scores
- Fix policy to check permission violations for required context categories
- Redefine context reduction metric to only count validated evidence (what's retained), not diagnostic metadata (what's rejected)

**Second test cycle**:
qwen3.7-plus implemented the fixes. I tested again:
- Decision accuracy: All 4 scenarios now produce correct decisions
- Context reduction: Improved to 33.0% in scenario 2, but still below 80% target

**Third test cycle**:
I accepted that 80% context reduction isn't achievable with the current heuristic claim extraction. Documented this as a known limitation rather than gaming the metric.

**Outcome**: Working implementation with all 4 scenarios producing correct decisions, 26/26 tests passing.

## Phase 4: Spec Compliance Review

**Tools**: Claude, Me

I provided Claude with:
- The initial specification (`docs/SPEC.md`)
- The final implementation code

Claude reviewed whether the code matches the specification and found two categories of mismatches:

**Missing context engineering principles**:
The code didn't explicitly demonstrate the 4 context engineering principles (Select, Write, Compress, Isolate) that I had added to the plan. The principles were implemented but not clearly documented or visible in the architecture.

**Technical spec mismatches**:
1. **Claim extraction**: Spec says LLM, code uses heuristic
2. **Unknown task type**: Spec says escalate, code returns default categories
3. **Retriever threshold**: Spec says escalate on low relevance, code doesn't
4. **Context reduction metric**: Was counting rejected items (fixed during testing)

**My response**:
I provided the fixes to qwen3.7-plus:
- Documented context engineering principles in README and code comments
- Documented technical mismatches as known limitations with rationale
- Context reduction metric was already fixed in Phase 3

**Outcome**: Spec-compliant implementation with transparent documentation of tradeoffs.

## Key Insights

1. **Multi-agent separation of concerns worked well**: Each tool had a clear role. My orchestration was critical to coordinating the agents and ensuring consistency across phases.

2. **Testing revealed issues that planning missed**: The first test cycle uncovered decision accuracy and metric issues that weren't caught during planning. Early testing is more valuable than extensive planning.

3. **Claude's review caught spec deviations that weren't obvious**: The technical mismatches were subtle deviations that qwen3.7-plus didn't notice. Having a separate review agent with the spec was valuable.

4. **Iterative refinement was necessary**: The project went through 3 test-fix cycles before reaching a working state. Future projects should test earlier and more frequently.

5. **Documentation of tradeoffs is critical**: Every deviation from the spec was documented with rationale, turning potential criticisms into defensible design choices.

## What I Would Do Differently

- **Test earlier**: Run the first test cycle during implementation, not after
- **Review spec compliance sooner**: Have Claude review the code against the spec after the first working version, not at the end
- **Define metrics more precisely**: The context reduction metric was ambiguous in the spec, leading to incorrect implementation
