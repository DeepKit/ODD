---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# Object Model

## Intent
All engineering activities in ODD revolve around five core objects: Contract, Task, Artifact, Evidence, and Seal.
Their complexity scales with the project level, but the core relationships remain unchanged: Contracts define Tasks, Tasks produce Artifacts, Gates generate Evidence, and Evidence supports Seals.

## Specification

### Object Relationship Diagram
```
Contract ──defines──→ Task ──produces──→ Artifact
                        │                   │
                   Gate Check           Seal Lock
                        │                   │
                        └──generates──→ Evidence ──binds──┘
```

### 1. Contract
A clear agreement on a piece of work. A Contract MUST be defined clearly before work begins.

### 2. Task
A specific work item under a Contract. Each Task produces one Artifact.

### 3. Artifact
A verifiable concrete deliverable (code, documentation, configuration, test report, etc.). Artifacts MUST be addressable and versioned.

### 4. Evidence
The result record of a Gate check. Long content MUST be offloaded to an Evidence object, with only a summary + `evidence_ref` injected into the context.

### 5. Seal
Locking the Artifact + Evidence set. Once sealed, it is immutable; any modification MUST first unseal, and unsealing MUST record the reason and trigger an audit.

---

## Mechanism

### L1 · Lightweight

Each object retains only the minimum necessary fields.

**Contract**:
```yaml
contract:
  id: string
  title: string
  acceptance_criteria: [string]     # At least 1 item
  boundary_cases: [string]          # At least 1 item
```

**Task**:
```yaml
task:
  id: string
  contract_id: string
  title: string
  state: pending | in_progress | review | done | rework
  acceptance_criteria: [string]
  depends_on: [task_id]
```

**Artifact**:
```yaml
artifact:
  id: string
  task_id: string
  type: string                      # Free naming
  path: string                      # For location
  depends_on: [artifact_id]
```

**Evidence**:
```yaml
evidence:
  type: test_report
  result: pass | fail
  summary: string
```

**Seal**: Archiving the artifact counts as sealing; no extra fields.

---

### L2 · Standard

Adds quality control and audit fields on top of L1.

**Contract Increment**:
```yaml
contract:
  # ...L1 fields...
  scope_in: string                  # What to do
  scope_out: string                 # What not to do
  error_cases: [{code, description}]
  quality_score: int                # Quality score (0-100)
  quality_details: object           # Score details
  human_confirmed: bool             # Human confirmation for key contracts
```

**Contract Quality Scoring Rules**:
| Check Item | Score | Description |
|---|---|---|
| Title Clarity | 10 | ≥ 10 chars and unambiguous |
| Description Completeness | 15 | ≥ 50 chars, includes background and goal |
| Acceptance Criteria Count | 20 | ≥ 3 items for full marks |
| Acceptance Verifiability | 15 | Each item has clear Given-When-Then |
| Boundary Case Coverage | 20 | ≥ 3 items, covering min/max/null values |
| Exception Definition | 15 | ≥ 1 item, with clear error codes |
| Security Level Label | 5 | Security level is labeled |

**Activation Thresholds**:
- ≥ 80 points: Can activate directly
- 60-79 points: Warning, suggestion to supplement
- < 60 points: Activation prohibited, must supplement

**Task Increment**:
```yaml
task:
  # ...L1 fields...
  state: blocked | pending | in_progress | quality_check | acceptance | done | rework
  task_level: L1 | L2
  artifact_type: string
  input_spec: string
  output_spec: string
  side_effects:                     # Required for behavior-type artifacts
    - type: string                  # Side effect type
      target: string                # Impact target
      description: string
  expected_effects:                 # Verifiable declaration of side effects (optional)
    - type: string
      target: string
      data_match: object?           # Expected fields/values to match
  rework_count: int
  failure_context:
    evidence_ref: string
    summary: string
```

**Side Effect Types**:
| Type | Description |
|---|---|
| db_read / db_write | Database read/write |
| cache_read / cache_write | Cache read/write |
| data_insert / data_update / data_delete | Data change (explicit) |
| event_emission | Event emission |
| message_publish / message_send | Message publish/send |
| notification_email / notification_sms | Notification sending |
| http_request / external_call | External call |
| file_read / file_write / file_create | File operation |
| log_write | Log writing |
| time_get / random_generate | Non-deterministic source |

**Artifact Increment**:
```yaml
artifact:
  # ...L1 fields...
  state: sealed | stale
  dependency_graph:
    upstream: [artifact_id]
    downstream: [artifact_id]
```

**Evidence Increment**:
```yaml
evidence:
  # ...L1 fields...
  evidence_type: test_report | coverage_report | lint_report | review_record
  storage_ref: string
  sha256: string
  gate: string                      # Associated gate
  contract_id: string
  task_id: string
```

**Seal Increment**:
```yaml
seal:
  artifact_version: string
  evidence_bundle: [evidence_ref]
  sealed_at: datetime
  sealed_by: string
```

---

### L3 · Strict

Adds adversarial generation, dynamic gate chains, and immutable sealing on top of L2.

**Contract Increment**:
```yaml
contract:
  # ...L2 fields...
  formal_spec:                      # Formal specification
    preconditions: [string]
    postconditions: [string]
    invariants: [string]
  temporal_config:                  # Temporal dimension
    lifecycle: string
    data_growth: string
    concurrency: string
    considerations: [string]?
    confirmed_by_human: bool?
  pk_history:                       # Adversarial generation record
    - round: int
      issue: string
      fix: string
      verdict: string

**Formal Syntax Rules (Simplified)**:
- Allowed: `== != > >= < <=`, `AND/OR/NOT`, `len()`, `regex_match()`, `in`, `IMPLIES`.
- Constraints must be verifiable, avoiding subjective words (e.g., "fast", "excellent").

**Formal Example**:
```yaml
formal_spec:
  preconditions:
    - "username != null"
    - "len(username) >= 3"
    - "regex_match(email, '.*@.*')"
  postconditions:
    - "result.success == true OR result.error != null"
    - "result.success == true IMPLIES result.token != null"
  invariants:
    - "user.password_hash != user.password_plain"
```

**Temporal Dimension Defaults** (One-click confirmable):
- lifecycle: temporary | short_term | medium_term | long_term (default: medium_term)
- data_growth: stable | linear | exponential (default: linear)
- concurrency: <10 | 10-100 | 100-1000 | >1000 (default: 10-100)
- considerations: i18n | multi_timezone | data_migration | offline_support (optional)

Human Confirmation Rules:
- If using defaults, can confirm with one click.
- If modifying defaults, MUST record `confirmed_by_human`.

```

**Task Increment**:
```yaml
task:
  # ...L2 fields...
  task_level: L1 | L2 | L3 | L4
  gate_chain: [string]              # Dynamic gate sequence
  developed_by_workshop_id: string  # For cross-review
```

**Artifact Increment**:
```yaml
artifact:
  # ...L2 fields...
  seal_hash: string                 # Hash pointing to seal record
```
Only `seal_hash` is kept on the artifact as a pointer; the complete seal record is in the independent seal object below.

**Evidence Increment**:
```yaml
evidence:
  # ...L2 fields...
  evidence_type: ...L2 types... | mutation_report | adversarial_report | cross_review_record | human_review_record
  mutation_score: float?
  vulnerability_count: int?
  reviewers: [string]?
  consensus: bool?
  workshop_id: string
```

**Seal Increment**:
```yaml
seal:
  # ...L2 fields...
  seal_hash: string                 # Immutable hash
  input_seal_hashes: [string]       # Upstream artifacts' seal_hash
  gate_results: [evidence_ref]      # All gate evidence
  audit_record_ref: string

unseal:
  reason: string                    # Unseal reason (bug description)
  by: string                        # Unseal authorizer (MUST be human)
  at: datetime
  count: int                        # Cumulative unseal count
```

**Unseal Rules**:
- Only humans can authorize unsealing; AI MUST NOT unseal on its own.
- MUST fill in the unseal reason.
- After unsealing, status becomes `rework`, and the originally sealed code is automatically archived.
- Unseal count accumulates, used for quality analysis (frequent unsealing indicates contract or testing quality issues).

**Unseal Process**:
```
Bug found → Human initiates unseal request (fills reason)
  → System records audit log
  → Originally sealed code archived
  → Status sealed → rework
  → unseal_count + 1
  → Normal rework process
```

---

## Practice

### Quick Selection
- **One person writing a small tool** → L1, 3-5 fields per object are enough.
- **Team collaboration** → L2, add quality control and dependency tracking.
- **Critical system / AI collaboration** → L3, full formal specifications, adversarial generation, evidence chains.

### Core Principles
- Object fields are cumulative: L2 is a superset of L1, L3 is a superset of L2.
- Relationships are invariant: Regardless of the level, the chain "Contract → Task → Artifact → Evidence → Seal" remains unchanged.
