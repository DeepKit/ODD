---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.03状态-State-Machine]
---

# Workshop Management Model

## Intent
Human decision load is constant, not growing with the number of workshops.
Whether 1 or 100 workshops run in parallel, humans only intervene at fixed decision points — contract definition, exception adjudication, final acceptance.

## Specification

### Role System
```
Human (Decision Maker)
  └── Architect (Designer, war-room five-role discussion)
        └── Manager (Monitor)
              └── Workshop (Container)
                    └── AI Worker (General Executor)
```

| Role | Does | Does not |
|------|------|----------|
| Human | Product decisions, contract confirmation, exception adjudication, unseal authorization | Does not write code, does not operate workshops |
| Architect | Requirement clarification, contract design, task decomposition | Does not execute tasks, does not monitor |
| Manager | Workshop start/stop, heartbeat monitoring, failure recovery, alerts | Does not assign specific tasks, does not intervene execution |
| Workshop | Process isolation, resource limits, heartbeat reporting, session management | Does not make business decisions |
| AI Worker | Task pickup, development, testing, sealing | Does not make architecture decisions, does not monitor other workshops |

### Peer Relationship
```
Contract ≈ Functional Module ≈ Workshop (1:1:1 binding)
```
One contract binds one functional module and is assigned to one workshop. The workshop executes all tasks of the contract in dependency order autonomously.

### AI Worker Role Switching
AI Worker is general-purpose, and switches roles by stage within a workshop:
- **Developer Worker**: writes code.
- **Test Worker**: writes unit tests, runs tests.
- **Integration Test Worker**: integration testing (executed by workers in other workshops, cross-review).
- **Sealing Worker**: code sealing (executed by workers in other workshops, cross-review).

**Cross-review Rule**: Integration testing and sealing MUST be performed by workshops other than the developer workshop. If the workshop pool has only one workshop, the system MUST issue an alert to humans.

---

## Mechanism

### L1 · Lightweight
**Single Workshop Mode.** No manager thread, no scheduling, humans manually switch tasks.

Suitable for: one person + one AI assistant small project. A workshop is the 'current working environment', no management needed.

---

### L2 · Standard
**Workshop Pool + Manager Scheduling.**

#### Workshop States
| State | Description |
|------|-------------|
| idle | Idle, can assign contracts |
| busy | Executing contract |
| offline | Offline/failure |

#### Manager Responsibilities
| Responsibility | Frequency |
|------|----------|
| Scheduling: find idle workshops, assign highest-priority contract | Periodic polling |
| Heartbeat monitoring: detect workshop liveness | Every 30 seconds |
| Failure recovery: on workshop failure, contract returns to queue | Event-driven |
| Timeout detection: task execution timeout, mark exception | Periodic check |
| Alerts: notify humans on issues | Event-driven |

#### Contract Queue
After contract activation it enters queue, ordered by priority (P0 > P1 > P2 > P3). Contracts recovered from failures automatically get priority +1.

#### Lifecycle
```
Contract Active (queued) → Manager Assigns (assigned) → Workshop Starts (active)
  → Execute Tasks → Contract Completed (completed) → Workshop Released to Pool
```

#### Failure Recovery
```
Workshop Executing → Heartbeat Lost → Manager Detects
  → Workshop marked offline
  → Contract returns to queue (priority +1)
  → Sealed tasks remain sealed
  → In-progress tasks reset to pending
  → New workshop takes over and continues
```

#### Task Interruption Handling
| Original Task State | State After Recovery |
|---------------------|----------------------|
| sealed | remain sealed |
| quality_check / acceptance / in_progress / rework | reset to pending |
| pending / blocked | unchanged |

#### Configuration Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| max_workshops | 3 | Max workshop pool size |
| heartbeat_interval | 30s | Heartbeat interval |
| heartbeat_timeout | 90s | Heartbeat timeout (3 misses) |
| task_timeout | 30min | Single task timeout |
| contract_timeout | 4h | Contract overall timeout |

---

### L3 · Strict
**Adds on top of L2: Knowledge Accumulation + VFS Persistence + Cross-review Quality Assurance.**

#### Workshop Knowledge Base
Each workshop has its own knowledge base; during sealing it extracts knowledge:
- Pattern Recognition
- Failure Lessons
- Best Practices
- Context Memory

New workshops can warm start by loading existing knowledge; target reuse rate > 70%.

#### VFS (Artifact Storage)
- Task state is persisted to database, not kept in workshop memory.
- Artifacts (code) are persisted to database.
- Workshop failures do not lose data; new workshops can resume.

#### Cross-review Quality Assurance

**Review Report MUST include**:
- reviewer_workshop_id
- result (passed / failed)
- checklist (items and results)
- issues (required when failed)

**Review Checklist**:
| Item | Weight |
|------|--------|
| ODD output match | 40% |
| Boundary coverage | 20% |
| Exception handling | 20% |
| Code conventions | 10% |
| Security scan | 10% |

**Review Quality Monitoring (SHOULD)**:
- Review duration < 5 minutes (too long may be perfunctory)
- Pass rate 60-90% (too high may be lax, too low may be too strict)
- Issue discovery rate > 10% (too low may be careless review)

#### Context Injection
Before executing tasks, the context engine (Intelligence Officer) pre-queries the DB and assembles context for one-time injection to AI:
```
Role + Stage + Task ID → Query Contracts/Specs/Functional Tree/Bug History/Best Practices → Trim by token budget → One-time injection to AI
```
Avoid AI making multiple tool calls with repeated full context (wasting tokens).

---

## Practice

### Quick Selection
- **One person + AI assistant** → L1, no workshop management needed.
- **Team collaboration, multiple contracts in parallel** → L2, workshop pool + manager scheduling + failure recovery.
- **AI multi-role collaboration, critical system** → L3, knowledge accumulation + VFS + cross-review QA.

### Core Principles
- **Human load is constant**: Adding workshops does not change number of human decision points.
- **Workshop autonomy**: Workshops decide task execution order, handle rework, collect evidence.
- **Failure does not lose progress**: State persistence + resume; workshop crash does not lose progress.
- **Cross-review**: A workshop must not review its own code — other workshops perform it.
