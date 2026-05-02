---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.02对象-Object-Model]
---

# Evidence, Sealing, and Auditing

## Intent
Saying "it's done" isn't enough — you need evidence.
Evidence is the product of gates, sealing is the endpoint of evidence, and auditing is the tamper-proof record.

## Specification

### Evidence-First Principle
- All gate conclusions MUST have re-verifiable evidence.
- Long outputs (logs, test reports, terminal sessions) MUST be externalized as evidence objects — they MUST NOT be inlined in context.
- Context MUST only inject: summary + evidence_ref.

### Sealing Rules
- Sealing MUST bind: artifact version + evidence bundle.
- After sealing, artifacts MUST be immutable; any modification MUST unseal first.
- Unsealing MUST record the reason, operator, and time, and trigger downstream re-verification.

### Auditing Rules
- Audit records MUST NOT be tamperable by executors.
- Any conclusion entering the knowledge base MUST carry source references (task_id / evidence_ref / version).

---

## Mechanism

### L1 · Lightweight

**Evidence**: The artifact itself is the evidence. A passing test report = evidence.
```yaml
evidence:
  type: test_report
  result: pass | fail
  summary: string
```

**Sealing**: Archiving the artifact counts as sealing. No additional process.

**Auditing**: No formal auditing. Version control history (e.g., git log) serves as the record.

---

### L2 · Standard

**Evidence**: Structured records — each evidence entry linked to a gate and task.
```yaml
evidence:
  id: string
  evidence_type: test_report | coverage_report | lint_report | review_record
  gate: string                        # Which gate this relates to
  result: pass | fail
  summary: string
  storage_ref: string                 # Storage location
  sha256: string
  contract_id: string
  task_id: string
```

**Sealing**: Explicitly binds artifact + evidence bundle.
```yaml
seal:
  artifact_version: string
  evidence_bundle: [evidence_id]
  sealed_at: datetime
  sealed_by: string
```

**Unsealing**:
```yaml
unseal:
  reason: string
  by: string
  at: datetime
```
After unsealing, downstream dependent artifacts are automatically marked as stale.

**Audit Log**: Records key operations (sealing, unsealing, gate results).
```yaml
audit_log:
  action: seal | unseal | gate_pass | gate_fail
  target_id: string
  by: string
  at: datetime
  details: string
```

**Evidence Retrieval**: The system SHOULD provide on-demand query capabilities (tail / grep / slice).

---

### L3 · Strict

**Evidence Enhancement**:
- Adds mutation testing, adversarial testing, cross-review, and human review evidence types.
- Evidence objects MUST include workshop_id (source workshop).

**Sealing Enhancement**:
- Generates seal_hash (hash of artifact content + evidence bundle) — tamper-proof.
- Includes seal_hash of all input artifacts (evidence chain propagation).
- Sealed state is irreversible (unlike L2's unsealable approach). To modify, a new version must be created.

```yaml
seal:
  seal_hash: string
  input_seal_hashes: [string]         # Upstream artifact seal_hashes
  evidence_refs: [string]
  gate_results: [evidence_ref]
  sealed_at: datetime
  audit_record_ref: string
```

**Auditing Enhancement**:
- Audit log MUST be immutable (append-only).
- Each audit record includes the hash of the previous record (chain integrity).
- Unseal operations MUST record cumulative count; abnormal unsealing SHOULD trigger alerts.

---

## Practice

### Quick Selection
- **Small projects** → L1: test report is evidence, archiving is sealing.
- **Team projects** → L2: structured evidence + audit log + unsealable.
- **Critical systems** → L3: tamper-proof audit chain + evidence chain propagation + irreversible sealing.

### Core Principles
- **Evidence is not inlined**: Long content is externalized as evidence objects; context uses only references.
- **Sealing is the endpoint**: A sealed artifact is definitive and trustworthy.
- **Auditing is tamper-proof**: Executors cannot modify their own audit records.
