---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.03状态-State-Machine, ODD.0F车间-Workshop-Model]
---

# Smart Racing

## Intent
Not choosing the best executor, but a sufficient one.
Use low-cost resources for simple tasks, upgrade on failure as needed — diagnose the cause first, then decide the upgrade path.

## Specification

### Core Principles
- Executor (model/human) selection MUST be based on task complexity; do not always use the strongest resource.
- After failure MUST diagnose the reason first, then decide upgrade path; blind upgrade is an anti-pattern.
- Costs SHOULD be observable, budgetable, and alertable.

### Failure Diagnosis First
Failure MUST be categorized into one of five reasons, with corresponding handling paths:
- **Context Insufficient**: Add context → retry at same level → does not consume upgrade count.
- **Contract Ambiguous**: Fix contract/task description → retry at same level → does not consume upgrade count.
- **Tests Unreasonable**: Review test validity → fix tests → retry at same level → does not consume upgrade count.
- **Executor Insufficient**: Upgrade executor → consumes upgrade count.
- **Unknown Issue**: Upgrade executor (conservative strategy) → consumes upgrade count.

Only Executor Insufficient and Unknown Issue trigger upgrades. Other reasons should be fixed at the same level.

### Upgrade Path
```
Junior ──Fail──→ Mid ──Fail──→ Senior ──Fail──→ Human Intervention
  │              │              │
  └──Success─────┴──Success─────┴──Success──→ Done
```
If the highest level still fails, MUST escalate to human decision.

---

## Mechanism

### L1 · Lightweight
No formal racing. Executor is fixed (human or specified model). After failure, humans decide whether to switch.

---

### L2 · Standard

**Task Grading**: Preselect executor level based on complexity.

Grading factors:
- Artifact type (config vs algorithm)
- Estimated LOC (< 50 vs > 200)
- Dependency count (0-2 vs > 5)
- Historical rework rate

```yaml
rules:
  - name: simple_task
    conditions:
      - artifact_type in [config, script, simple_query]
      - estimated_lines < 50
    executor_level: junior

  - name: standard_task
    conditions:
      - artifact_type in [code_module, api_endpoint]
      - estimated_lines < 200
      - dependencies < 3
    executor_level: standard

  - name: complex_task
    conditions:
      - artifact_type in [algorithm, architecture]
      - or: rework_count > 1
    executor_level: senior
```

**Failure Escalation**: Auto-upgrade by rework count.
- 0-1 reworks: junior.
- 2-3 reworks: mid.
- 4-5 reworks: senior.
- ≥6 reworks: trigger human alert (see `ODD.0D预警-Alert-Traffic-Light.md`).

**Diagnosis**: On failure, system records failure type (compile error/test failure/acceptance failure/timeout) for human reference.

---

### L3 · Strict

**Intelligent Diagnosis**: After failure, a diagnostician (Manager AI or rules engine) analyzes root cause and decides handling path.

```
Task Fails
  │
  ├── Cause A: Context Insufficient
  │     → Add context (from knowledge base/functional tree/dependency graph)
  │     → Retry at same level
  │     → Does not consume upgrade count
  │
  ├── Cause B: Contract Ambiguous
  │     → Trigger clarity re-assessment (see `ODD.06对抗-Contract-Adversarial.md`)
  │     → Fix and retry at same level
  │     → Does not consume upgrade count
  │
  ├── Cause C: Tests Unreasonable
  │     → Review test validity (Mutation score too low? Tests mismatch contract?)
  │     → Fix tests then retry at same level
  │     → Does not consume upgrade count
  │
  ├── Cause D: Executor Insufficient
  │     → Upgrade to higher-level executor
  │     → Consumes upgrade count
  │
  └── Cause E: Unknown Issue
        → Upgrade executor (conservative strategy)
        → Consumes upgrade count
```

**Cost Monitoring**:
- System SHOULD record executor level, call count, upgrade count per task.
- System SHOULD provide aggregated views: first-pass success rate, upgrade success rate, human intervention rate.
- When upgrade rate > 30%, SHOULD trigger alert to check grading rules or contract quality.

**Data Structure**:
```yaml
task_execution:
  task_id: string
  executor_level: junior | standard | senior
  rework_count: int
  upgrade_count: int                    # Actual consumed upgrade count
  diagnosis_history:
    - attempt: 1
      failure_type: test_failed
      diagnosis: context_insufficient
      action: inject_context
    - attempt: 2
      failure_type: test_failed
      diagnosis: executor_insufficient
      action: upgrade_executor
  cost: float                           # Execution cost
```

---

## Practice

### Quick Selection
- **Personal project** → L1, fixed executor, manual decision.
- **Team project** → L2, complexity grading + auto-upgrade.
- **AI multi-role collaboration** → L3, intelligent diagnosis + on-demand upgrade + cost monitoring.

### Core Principles
- **Sufficient is enough**: Choose the most suitable, not the strongest. 80% of tasks do not need the strongest executor.
- **Diagnose before upgrade**: 60% of failures are not executor issues (Context 60% + Contract 30% + Executor 10%).
- **Cost visibility**: Without cost monitoring, cost cannot be optimized.
