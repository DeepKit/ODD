---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: []
---

# Template Library

## Intent
Copy → Fill → Start. Choose templates by level, don't start from scratch.

## Specification
- Select templates consistent with the project level; do not use cross-level templates.
- Template fields may be extended, required fields MUST NOT be removed.
- Fill acceptance criteria and boundaries first, then implement.

## Mechanism

---

## L1 · Lightweight Templates

### Contract
```yaml
contract:
  title: ""
  acceptance_criteria:
    - ""
  boundary_cases:
    - ""
```

### Task
```yaml
task:
  title: ""
  contract_id: ""
  acceptance_criteria:
    - ""
  depends_on: []
```

### Artifact
```yaml
artifact:
  type: ""
  path: ""
  depends_on: []
```

---

## L2 · Standard Templates

### Contract
```yaml
contract:
  title: ""
  scope_in: ""
  scope_out: ""
  acceptance_criteria:
    - given: ""
      when: ""
      then: ""
  boundary_cases:
    - ""
  error_cases:
    - code: ""
      description: ""
  human_confirmed: false
```

### Task
```yaml
task:
  title: ""
  contract_id: ""
  artifact_type: ""
  artifact_name: ""
  artifact_path: ""
  input_spec: ""
  output_spec: ""
  acceptance_criteria:
    - ""
  error_cases:
    - ""
  depends_on: []
  task_level: L1
```

### Evidence
```yaml
evidence:
  evidence_type: ""
  gate: ""
  result: pass | fail
  summary: ""
  storage_ref: ""
  sha256: ""
  contract_id: ""
  task_id: ""
```

### Seal
```yaml
seal:
  artifact_version: ""
  evidence_bundle: []
  sealed_at: ""
  sealed_by: ""
```

### Rework Context (Required during rework)
```yaml
failure_context:
  rework_number: 1
  from_status: ""
  failure_reason: ""
  failure_evidence_refs: []
  previous_attempts:
    - ""
```

---

## L3 · Strict Templates

### Contract (Add on top of L2)
```yaml
contract:
  # ...L2 fields...
  formal_spec:
    preconditions: []
    postconditions: []
    invariants: []
  temporal_config:
    lifecycle: ""
    data_growth: ""
    concurrency: ""
  pk_history:
    - round: 1
      issue: ""
      fix: ""
      verdict: ""
```

### Task (Add on top of L2)
```yaml
task:
  # ...L2 fields...
  task_level: L1 | L2 | L3 | L4
  gate_chain: []
  developed_by_workshop_id: ""
```

### Seal (Add on top of L2)
```yaml
seal:
  # ...L2 fields...
  seal_hash: ""
  input_seal_hashes: []
  gate_results: []
  audit_record_ref: ""
```

### Audit Log
```yaml
audit_log:
  action: seal | unseal | gate_pass | gate_fail
  target_id: ""
  by: ""
  at: ""
  previous_hash: ""
  details: ""
```

---

## General Templates (Cross-level)

### Pipeline
```yaml
pipeline:
  id: ""
  name: ""
  description: ""
  inputs:                              # Sealed artifacts
    - artifact_id: ""
      seal_version: ""
  stages:
    - name: ""
      contract_id: ""
      task_ids: []
  output:
    artifact_id: ""
    artifact_type: ""
  depends_on_pipelines: []
```

### Functional Node
```yaml
functional_node:
  id: ""
  name: ""
  parent: ""                           # null for root
  children: []
  artifacts: []                        # Mapped artifact IDs
  owner: ""
  status: active | deprecated | planned
```

### CAP Record
```yaml
cap_record:
  contract_id: ""
  clarity_detect:
    overall: clear | slightly_unclear | very_unclear
    score: 0
    action: pass | suggest | must_answer
    issues:
      - type: ""
        description: ""
        severity: green | yellow | red
    human_answers: []
  pk_history:
    - round: 1
      attacker: Challenger | Attacker
      attack_vector: logic | boundary | malicious
      issue: ""
      fix: ""
      verdict: pass | escalate
```

### Bug Pattern Entry
```yaml
bug_pattern:
  id: ""
  artifact_type: ""
  pattern: ""
  detection_rule: ""
  severity: critical | high | medium | low
  frequency: 0
  prevention: ""
  source_task_id: ""                   # First found task
```

### Best Practice Entry
```yaml
best_practice:
  id: ""
  artifact_type: ""
  practice: ""
  rationale: ""
  anti_pattern: ""
  priority: 1                          # 1-10
  is_mandatory: false
```

### Workshop
```yaml
workshop:
  id: ""
  contract_id: ""
  status: idle | active | paused | failed | completed
  assigned_to: ""                      # Executor (Human/AI)
  task_ids: []
  knowledge_cache: []                  # Workshop-level knowledge cache
  created_at: ""
  last_active_at: ""
```

### Alert Event
```yaml
alert:
  id: ""
  level: green | yellow | red
  source: ""
  message: ""
  triggered_at: ""
  acknowledged_by: ""
  resolution: ""                       # Handling result
```

### Racing Assignment
```yaml
racing_assignment:
  task_id: ""
  task_grade: L1 | L2 | L3 | L4
  assigned_level: ""
  attempt: 1
  max_attempts: 3
  failure_diagnosis: ""
  escalated: false
  escalated_to: ""
```

---

## Practice
- Small projects: use L1 directly.
- Team collaboration: start with L2, choose general templates as needed.
- Critical systems: use L3 and add formal_spec + temporal_config, and use all general templates.
