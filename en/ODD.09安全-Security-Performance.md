---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# Security and Performance Contracts

## Intent
Security and performance are not "deal with it later" concerns — they are part of the contract.
Written into the contract, they can be verified through gates; not written, they are never checked.

## Specification

### Security Principles
- Sensitive fields MUST be masked (output filtering).
- Long outputs MUST be converted to evidence (evidence_ref) — they MUST NOT flow as plaintext into context.
- Security rules are hard context boundaries and MUST be forcibly injected.

### Performance Principles
- Performance requirements SHOULD be written into contracts using testable metrics.
- Performance verification SHOULD be implemented through gates (testing/monitoring).

---

## Mechanism

### L1 · Lightweight

**Security**: Basic awareness is sufficient.
- Don't hardcode passwords/keys.
- Validate inputs.
- Use parameterized SQL queries.

**Performance**: No formal performance contract. "Works fine" is enough.

---

### L2 · Standard

**Security Layering**:
- **API Layer**: Input format validation + authentication (JWT/API Key).
- **Pipeline Layer**: Authorization checks (RBAC) + business preconditions.
- **DB Layer**: Constraints (CHECK/FK/triggers) as the last line of defense.

**Performance Contract**: Written in contracts using testable metrics.
```yaml
performance:
  latency:
    p50: 100ms
    p95: 500ms
    p99: 1s
  throughput:
    target: 100 req/s
  timeout: 5s
  resources:
    max_memory: 512MB
    max_rows_scanned: 10000
```

**Performance Verification**: Performance tests serve as gate evidence.

---

### L3 · Strict

**Security Enhancement**:
- Add RLS (Row-Level Security).
- Write sensitive data masking strategies into contracts.
- Security-related artifacts automatically escalate task_level (triggering stricter gate chains).

**Performance Enhancement**:
- Benchmarks become part of seal evidence.
- Runtime monitoring continuously verifies performance contracts.
- Define degradation strategies (fallback plans for timeout/overload).
```yaml
performance:
  # ...L2 fields...
  benchmark:
    dataset_size: "1 million rows"
    expected_latency_p95: 200ms
  degradation:
    strategy: "circuit_breaker"
    fallback: "Return cached results"
    threshold: "p99 > 2s for 5 consecutive times"
```

---

## Practice

### Quick Selection
- **Small projects** → L1: basic security awareness, no performance contract.
- **Team projects** → L2: three-layer security + testable performance metrics.
- **Critical systems** → L3: RLS + benchmarks + degradation strategies.

### Core Principles
- **Security belongs in the contract**: If it's not written, no one checks.
- **Performance must be testable**: "Fast" is not a metric; "p95 < 500ms" is.
- **DB is the last line of defense**: Upper layers may have bugs, but DB constraints ensure data integrity.
