---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# Execution Model

## Intent
ODD is not only artifact-driven, it must also answer: what to do on errors? how to control side effects? how do states flow? how is concurrency constrained? how are transactions and compensations split?
The execution model pushes these questions to the contract and pipeline layers, ensuring verifiable, recoverable, and auditable execution.

## Specification

### Error Model
Errors MUST be explicitly classified and declared:
- **Recoverability**: recoverable / unrecoverable
- **Responsibility**: client_error / server_error / external_error
- **Propagation**: upstream errors MUST be declared or transformed downstream; silent swallowing is not allowed

### Side-Effect Model
- Side effects MUST be explicitly declared (`effects`) and bound to verification rules.
- Any external call MUST declare retry/timeout/idempotency strategy.

### State Model
- State can be explicitly passed as input/output, or declared as state containers (reads/writes).
- Complex state SHOULD be described with state machine contracts.

### Concurrency Model
- Concurrency strategy MUST be explicit: serialized / parallel / locked.
- Idempotency MUST be declared: idempotency key, behavior, TTL.

### Transactions and Compensation
- DB transactions contain only DB operations; external calls must be outside the transaction.
- Cross-step failures MUST have compensation strategies (reverse undo or state rollback).

---

## Mechanism

### L1 · Lightweight

**Minimal declarations**:
- Errors only distinguish recoverable / unrecoverable.
- Side effects are text descriptions only.
- Concurrency defaults to serialized.

```yaml
contract:
  errors:
    - code: INVALID_INPUT
      recoverable: false
  effects:
    - type: db_write
      description: "Insert user record"
```

---

### L2 · Standard

**Error classification + explicit propagation**:
```yaml
errors:
  - code: INVALID_EMAIL
    category: client_error
    recoverable: false
    message: "Invalid email format"
  - code: DB_TIMEOUT
    category: external_error
    recoverable: true
    retry_strategy: exponential_backoff
    max_retries: 3

error_propagation:
  mode: explicit          # explicit | transform
  mapping:
    DB_TIMEOUT -> SERVICE_TEMPORARY_UNAVAILABLE
```

**Side-effect declaration and verification**:
```yaml
effects:
  - type: db_write
    target: users
    operation: insert
  - type: event_emit
    event: user_created

expected_effects:
  - type: db_write
    target: users
    data_match:
      email: "test@example.com"
```

**State container**:
```yaml
state_container Session:
  scope: session
  schema:
    user_id: uuid
    token: string

contract GetProfile:
  reads: [Session.user_id]
  output: { profile }
```

**Concurrency and idempotency**:
```yaml
concurrency:
  mode: serialized
  lock_key: email
  lock_timeout: 5s

idempotency:
  enabled: true
  key: email
  behavior: return_existing
  ttl: 24h
```

---

### L3 · Strict

**Transaction boundaries + compensation strategy**:
```yaml
transaction:
  isolation: serializable
  timeout: 30s
  steps:
    - contract: CreateOrder
    - contract: ProcessPayment
    - contract: SendConfirmation
  on_failure:
    strategy: rollback_all | compensate
    compensations:
      - CreateOrder: CancelOrder
      - ProcessPayment: RefundPayment
```

**Hybrid pipeline modes**:
- **Orchestration**: Application layer coordinates multiple steps.
- **Choreography**: DB emits events, application layer responds.
- **Saga**: Each step has compensation, execute compensations in reverse on failure.

**Execution context**:
```yaml
execution_context:
  request_id: string
  timestamp: datetime
  errors: [error]
  effects: [effect]
  transaction_id: string?
```

---

## Practice

### Quick Selection
- **Small project** → L1, minimal error and side-effect declarations.
- **Team collaboration** → L2, error classification + idempotency + state containers.
- **Critical system** → L3, transaction boundaries + compensation + Saga.

### Core Principles
- **Errors must not be invisible**: If not declared, they do not exist.
- **Side effects must be verifiable**: Otherwise you cannot prove they really happened.
- **Transactions should be short, compensations clear**: Long transactions inevitably lock the system.
- **Concurrency must be controllable**: Locks and idempotency are the lowest-cost insurance.
