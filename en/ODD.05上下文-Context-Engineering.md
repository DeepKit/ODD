---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.02对象-Object-Model]
---

# Context Engineering

## Intent
Give the executor (human or AI) information that is just right: not too much, not too little, and with traceable sources.
Too much wastes tokens and attention; too little leads to wrong decisions.

## Specification

### Context Principles
- **Minimal Necessary Injection**: Only give information needed for the current task.
- **No Inline Evidence**: Long content MUST be offloaded to evidence objects, referenced by `evidence_ref`.
- **Traceable Source**: Every piece of context MUST be labeled with its source (which contract/task/evidence).
- **Rework Forced Injection**: When reworking, MUST inject `failure_context` (including `evidence_refs`).

---

## Mechanism

### L1 · Lightweight

**Context = Manually Prepared.**

Before executing a task, manually confirm the following information is available:
- Contract acceptance criteria
- Task input/output specifications
- Location of dependent artifacts

No automation, no token control. Suitable for manual development.

---

### L2 · Standard

**Context = Functional Tree Query + Auto Injection + Token Control.**

**Functional Tree Query**:
Starting from the functional tree, precisely locate artifacts, contracts, and evidence relevant to the current task, rather than feeding the entire project to the executor.

**Injection Layering**:
- **Forced Injection**: Security rules + Architecture constraints + Task specs + Acceptance criteria.
- **On-Demand Injection**: Relevant code snippets + Bug patterns + Best practices (see `ODD.0E法宝-Bug-Map-Best-Practices.md`).
- **Rework Injection**: `failure_context` + History of attempts (to avoid repeating the same mistakes).

**Token Control**:
- System SHOULD have a token budget, trimming low-value content by priority.
- Priority: Security Rules > Task Specs > Acceptance Criteria > Relevant Code > Best Practices.

---

### L3 · Strict

**Context = Multi-Layer Injection + Workshop Knowledge Base + Dual-Stream Memory.**

**Multi-Layer Context Model**:
- Hard Boundary Layer: Security rules, architecture constraints, process norms — forced injection, impenetrable.
- Functional Tree Layer: Index query, locating relevant artifacts.
- Dependency Graph Layer: Querying upstream/downstream relationships.
- Knowledge Base Layer: Semantic knowledge extracted during workshop sealing (Bug patterns, best practices, implicit requirements; see `ODD.0E法宝-Bug-Map-Best-Practices.md`).
- Task Execution Layer: Task specs, acceptance, rework feedback.

**Intelligence Officer**:
- Role: Before calling the model, unifies database queries and assembles context to avoid "multiple calls + repeated context".
- Input: Role, Stage, `task_id`, `contract_id`, `module_id`.
- Output: Assembled context + Source metadata + Token estimation.

**Intelligence Officer Process**:
```
Task Assigned → IO Receives → Query DB (By Role/Stage)
  → Filter & Trim (Token Budget) → Layer Assembly → One-time Injection to Model
```

**17-Layer Context Model (Simplified)**:
- L1 Security Hard Boundary (P0)
- L2 Architecture Hard Boundary (P0)
- L3 Process Hard Boundary (P0)
- L4 System Level Specs (P1)
- L12 Workshop Knowledge Base: Bug Patterns/Best Practices (P1)
- L14 Task Specs (P0)
- L15 Acceptance & Testing (P0)
- L16 Execution Context/Relevant Code (P2)
- L17 Correction Feedback (P0, during rework)
Remaining layers expanded by project, principle is "Necessity First".

**Role View Matrix (Simplified)**:
- Architect: Global architecture, contract list, functional tree overview; does not see implementation details.
- Manager: Contract status, task scheduling, resource allocation; does not see code details.
- Workshop: Current module context/specs/execution info; does not see other modules' code.
- Worker: Current task spec/acceptance/execution context; does not see other tasks.

**Stage Injection Matrix (Simplified)**:
- Contract Generation: Functional tree overview + Relevant contract list.
- Clarity Check: Contract details + Ambiguity word bank + Historical ambiguity issues.
- Task Generation: Contract details + Dependencies + Sealed artifacts.
- Dev/Test/Review: Task specs + Acceptance criteria + Relevant code + Bug history + Best practices.

**Prompt Template Skeleton**:
```
## Hard Boundary (P0)
{L1_security_boundary}
{L2_architecture_boundary}
{L3_process_boundary}

## Expert Identity
{expert_identity}

## Task Specs (P0)
{L14_task_spec}
{L15_acceptance_criteria}

## Knowledge Base (P1)
{L12_bug_patterns}
{L12_best_practices}

## Correction Feedback (during rework)
{L17_failure_context}

## Relevant Code (P2)
{L16_code_context}
```

**Token Budget Suggestions**:
- Contract Constraints 200, Task Specs 300, Acceptance Criteria 200 (P0).
- Bug History 300, Best Practices 300 (P1).
- Relevant Code 500 (P2).
Trim by priority when over budget.

**Preset Parameter Groups** (Example):
- `full_injection` (Test stage, full amount)
- `minimal` (Save Tokens)
- `expert_focus` (Reinforce expert identity)
- `bug_prevention` (Reinforce Bug history)
- `rework_focus` (Reinforce correction feedback)
- `balanced` (Production environment)

**Prompt Storage Rules**:
- Prompts MUST be stored in DB, version managed, roll-backable and statistical.
- Record usage: Success rate, rework rate, token consumption.

**Workshop Knowledge Base**:
- Every workshop SHOULD extract knowledge to the knowledge base during sealing (Episodic Memory + Semantic Memory).
- New workshops SHOULD load relevant knowledge upon startup (Warm Start).
- Warm Start MUST verify knowledge version matches current artifact version.

**Dual-Stream Memory**:
- Episodic Memory (Short-term): Key decisions, problems encountered during this execution.
- Semantic Memory (Long-term): Patterns, laws, best practices precipitated across tasks.

**Monitoring Metrics** (SHOULD):
- `tokens_injected` / `tokens_saved`
- `layers_included` / `layers_skipped`
- `cache_hit_rate`
- `task_success` / `rework_count`

---

## Practice

### Quick Selection
- **Manual Dev, Small Project** → L1, manually confirm context is sufficient.
- **Team Collaboration, AI Assisted** → L2, Functional Tree Query + Token Control.
- **AI Multi-Role Collaboration** → L3, Multi-Layer Injection + Workshop Knowledge Base + Dual-Stream Memory.

### Core Principles
- **Minimal Necessary**: Give enough information, no more.
- **Traceable Source**: Every piece of context can be traced to its origin.
- **Rework Must Inject**: Failure information cannot be lost, otherwise the same mistake will be repeated.
