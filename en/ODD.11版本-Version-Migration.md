---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# Contract Version Migration

## Intent
Contracts evolve, but consumers may still use older versions.
A versioning strategy is required to define versions, maintain backward compatibility, plan deprecation paths, and design migration schemes.

## Specification

### Semantic Versioning
Contract versions MUST use the `MAJOR.MINOR.PATCH` format:

| Segment | Change Type | Example |
|----|----------|------|
| MAJOR | Breaking change (remove field, change type) | 1.1.1 → 2.0.0 |
| MINOR | Backward-compatible addition (new optional field) | 1.0.0 → 1.1.0 |
| PATCH | Bug fix (no contract structure change) | 1.1.0 → 1.1.1 |

### Compatibility Rules

**Backward-compatible changes (safe)**:
- ✅ Add optional input fields (MUST have default values)
- ✅ Add output fields
- ✅ Relax input constraints
- ✅ Add optional error codes

**Breaking changes (risky)**:
- ❌ Remove input/output fields
- ❌ Change field types
- ❌ Add required input fields
- ❌ Tighten input constraints
- ❌ Change field semantics (e.g., unit changes from cents to dollars)

Breaking changes MUST bump MAJOR.

### Version Lifecycle
```
CURRENT → DEPRECATED → SUNSET → REMOVED
  │           │           │          │
Normal Use   Warning     Reject      Code Removed
```

- DEPRECATED period SHOULD be ≥ 3 months (critical systems ≥ 6 months).
- After SUNSET, MUST return a clear error with upgrade guidance.

---

## Mechanism

### L1 · Lightweight

**No formal version management.** Modify contracts directly and manually notify affected parties.

Suitable for single-person projects, with few changes and no external consumers.

---

### L2 · Standard

**Contract carries version + Compatibility checks.**

Contract incremental fields:
```yaml
contract:
  version: "1.0.0"
  deprecated: false
  sunset_date: null
```

Tasks bind contract version:
```yaml
task:
  contract_version: "1.0.0"
```

#### Compatibility Check
When creating a new contract version, the system MUST automatically check compatibility:
- Compare input_spec / output_spec across versions.
- Removing fields, changing types, adding required fields → mark as breaking change.
- Breaking changes MUST be human-confirmed before submission.

#### Three Migration Modes

**Adapter Mode** (small diffs, auto-convertable):
```
Old Contract Call → Adapter Convert → New Contract Execute → Adapter Convert → Old Format Response
```
- Input conversion: fill defaults for new fields.
- Output conversion: drop fields unknown to old version.

**Expand-Contract Mode** (rename fields, restructure):
```
Phase 1: Expand — support both new and old fields (MINOR version)
Phase 2: Deprecate — old fields marked deprecated
Phase 3: Contract — remove old fields (MAJOR version)
```

**Version Routing Mode** (large diffs, cannot adapt):
```
Request carries version → route to corresponding implementation
```
- If version not found, route to closest compatible version.

---

### L3 · Strict

**Adds on top of L2: Deprecation middleware + Migration tracking + DB layer versioning.**

#### Deprecation Middleware
- DEPRECATED version: process requests normally, but response headers add `Deprecation: true` + `Sunset: <date>`.
- SUNSET version: reject requests, return 410 Gone + upgrade guidance.
- All consumers using deprecated versions MUST be recorded and notified.

#### Migration Tracking
```yaml
migration_tracking:
  version: "1.0.0"
  status: current | deprecated | sunset | removed
  deprecated_at: datetime?
  sunset_at: datetime?
  active_consumers: int        # Number of active consumers
  migration_guide_ref: string  # Migration guide reference
```

- The system MUST track usage per version.
- Before SUNSET, MUST confirm active_consumers = 0 (or manually confirm forced offboarding).

#### DB Layer Versioning
- Stored procedures/functions SHOULD carry version suffixes (e.g., `create_user_v1`, `create_user_v2`).
- Schema migration follows expand-contract mode: ADD COLUMN first, DROP COLUMN later.
- DROP COLUMN MUST be executed only after confirming no callers.

---

## Practice

### Quick Selection
- **Small project** → L1, modify directly, manual notification.
- **Team project** → L2, versioned + compatibility check + three migration modes.
- **Critical system** → L3, deprecation middleware + migration tracking + DB layer versioning.

### Core Principles
- **Design for evolution**: Name fields with foresight, use extensible structures.
- **Assess impact before change**: Run compatibility checks, analyze consumers.
- **Progressive migration**: Expand first, then contract; provide enough deprecation period.
- **Proactive communication**: Do not wait for consumers to hit issues; push migration info proactively.
