---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.02对象-Object-Model]
---

# State Machine and Gates

## Intent
Every state transition MUST have a reason, evidence, and a record.
Artifacts that have not passed a Gate are not allowed to flow downstream.

## Specification

### Basic Definitions
- **State**: Location identifier of an artifact in its lifecycle.
- **Gate**: Checkpoint between states, deciding whether transition is allowed.
- **Evidence Binding**: Every pass through a Gate MUST be associated with at least one evidence record.
- **Rework**: The fallback path when a Gate is not passed, MUST carry `failure_context`.

### State Transition Rules
- Transition = Gate Check + Evidence Binding + Audit Record; none can be missing.
- `failure_context` MUST reference an evidence object (`evidence_ref`) and MUST NOT inline large logs.
- `task_level` determines which Gates need to be passed; manual override MUST only upgrade, not downgrade.

---

## Mechanism

### L1 · Lightweight

**State Machine**:
```
pending → in_progress → review → done
           ↖── rework ──↙
```

**Gate**: Only one — `review`.
- Pass condition: Automated tests all pass.
- Evidence: Test report (pass/fail + coverage).
- Failure handling: Return to `in_progress`, with failure reason summary.

**Minimal Data Structure**:
```yaml
task:
  id: string
  state: pending | in_progress | review | done | rework
  evidence:
    - type: test_report
      result: pass | fail
      summary: string
```

---

### L2 · Standard

**State Machine**: Adds `blocked` and `quality_check` to L1.
```
blocked → pending → in_progress → quality_check → acceptance → done
                      ↖──────── rework ────────↙
```

**Gates**: Two — `quality_check` + `acceptance`.
- `quality_check` (Automated):
  - Pass condition: Tests pass + Coverage ≥ Threshold + Static analysis has no critical items.
  - Evidence: Test report + Coverage report + Lint report.
- `acceptance` (Manual):
  - Pass condition: Reviewer confirms artifact meets contract acceptance criteria.
  - Evidence: Review record (Reviewer ID + Verdict + Remarks).

**Rework Enhancement**:
- `rework` record contains: Triggered gate, failed evidence reference, rework count.
- When rework count ≥ 3, SHOULD automatically upgrade `task_level`.

**Data Structure Increment**:
```yaml
task:
  # ...L1 fields...
  state: blocked | pending | in_progress | quality_check | acceptance | done | rework
  task_level: L1 | L2
  rework_count: int
  evidence:
    - type: test_report | coverage_report | lint_report | review_record
      gate: quality_check | acceptance
      result: pass | fail
      reviewer_id: string?      # Filled for manual gates
      failure_context:
        evidence_ref: string    # Points to specific evidence ID
        summary: string
```

---

### L3 · Strict

**State Machine**: Adds risk-driven dynamic gate chains to L2.
```
blocked → pending → in_progress → quality_check
  → [mutation_test] → [adversarial_test] → [cross_review] → [human_review]
  → acceptance → sealed
       ↖──────────────── rework ────────────────↙
```

Square brackets = Dynamically inserted based on `task_level`:
- L1 Task: Skips all extended gates.
- L2 Task: Inserts `mutation_test`.
- L3 Task: Inserts `mutation_test` + `adversarial_test`.
- L4 Task: Inserts all, including `human_review`.

**Gate Details**:
- `mutation_test`:
  - Pass condition: `mutation_score` ≥ Threshold (suggested 80%).
  - Evidence: Mutation test report (surviving mutants list + total score).
- `adversarial_test`:
  - Pass condition: No high-risk vulnerabilities survive.
  - Evidence: Vulnerability list + reproduction experiment records.
- `cross_review`:
  - Pass condition: Multi-party reviewer consensus (≥ 2/3 pass).
  - Evidence: Opinions from all parties + basis for verdict.
  - Report Structure:
    ```yaml
    cross_review_report:
      reviewers: [workshop_id]       # Participating workshops
      opinions:
        - reviewer: workshop_id
          verdict: pass | fail | concern
          comments: [string]
      consensus: bool                # Whether consensus was reached
      escalated: bool                # Whether escalated to human
      escalation_reason: string?     # Description of disagreement
    ```
- `human_review`:
  - Trigger condition: `cross_review` disagreement, or `task_level` = L4.
  - Evidence: Human verdict record + reason.

**Sealed**:
- `done` upgrades to `sealed` — state is irreversible, evidence chain is frozen.
- `sealed` MUST generate `seal_hash`, binding all `evidence_refs`.

**Data Structure Increment**:
```yaml
task:
  # ...L2 fields...
  state: ...L2 states... | mutation_test | adversarial_test | cross_review | human_review | sealed
  task_level: L1 | L2 | L3 | L4
  gate_chain: [string]           # Dynamically generated gate sequence
  seal:
    seal_hash: string
    sealed_at: datetime
    evidence_refs: [string]      # All evidence IDs
  evidence:
    - type: ...L2 types... | mutation_report | adversarial_report | cross_review_record | human_review_record
      gate: string
      result: pass | fail
      mutation_score: float?
      vulnerability_count: int?
      reviewers: [string]?
      consensus: bool?
```

---

## Practice

### Quick Selection Guide
- **I'm writing a small tool alone** → Use L1, 4 states are enough.
- **Team collaboration, with code review process** → Use L2, add manual acceptance gate.
- **AI multi-role collaboration, critical system** → Use L3, add dynamic gate chains and sealing.

### task_level Grading Algorithm

AI auto-grading + Human override. Done automatically at task creation, saved after human confirmation.

**Four-Dimension Scoring**:
| Dimension | L1 (1 pt) | L2 (2 pts) | L3 (3 pts) | L4 (4 pts) |
|---|---|---|---|---|
| Est. LOC | < 30 | 30-100 | 100-300 | > 300 |
| Function Complexity | Single table CRUD | Multi-table relation | Complex algorithm | Distributed/Concurrent |
| Security Sensitivity | None | Low (Logs) | Medium (User Data) | High (Auth/Payment) |
| External Dependencies | 0 | 1-2 | 3-5 | > 5 |

**Calculation Rule**: `Final Level = MAX(Dimension Levels)` — Short-board principle, any single high-risk dimension will not be diluted by other low-risk dimensions.

**Human Override Rules**:
- Humans can manually adjust the level, **can only upgrade, cannot downgrade**.
- Downgrading requires entering a reason and recording an audit log.

### Verification Strategy Classification

`artifact_type` determines the verification strategy, and the verification strategy determines which states to skip:

| Strategy | quality_check | acceptance | mutation_test | Applicable |
|---|---|---|---|---|
| automated | Auto Unit Test | Auto Integration Test | Execute | Code types |
| executed | Execution Verification | Effect Verification | Skip | Database/Behavior types |
| reviewed | Format Check | Manual Review | Skip | Document types |
| single | Skip | Combined Verification | Skip | Simple Config |
| none | Skip | Skip | Skip | Comments/Logs |

### External Display Labels

Internal states are unified, external display uses professional terms based on artifact category:

| Internal State | Code Type | Database Type | Behavior Type | Doc Type | Config Type |
|---|---|---|---|---|---|
| in_progress | Developing | Developing | Developing | Drafting | Configuring |
| quality_check | Unit Testing | DDL Executing | Trigger Verifying | Format Checking | Syntax Verifying |
| acceptance | Integration Testing | Data Verifying | Effect Verifying | Content Reviewing | Effect Verifying |
| mutation_test | Mutation Testing | Mutation Testing | Mutation Testing | Skip | Skip |

States not listed (blocked/pending/sealed/rework) have the same labels across categories.

### Adaptation Suggestions
- Can mix levels by module: Core module L3, tool scripts L1.
- Gate thresholds (coverage, mutation_score, etc.) are set by the project; ODD does not prescribe specific values.
