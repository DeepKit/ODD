---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# Pipeline and Composition

## Intent
Artifacts are not isolated. Atomic artifacts are promoted into new artifacts through pipeline composition; this is how the Hive grows.
A Pipeline is an assembly line with a contract—it declares what it receives, what it produces, and what constitutes success.

## Specification

### Pipeline Definition
Pipeline = Reusable unit of "Input Artifacts → Transformation → Output Artifact".
Each Pipeline MUST have its own contract, declaring:
- Input: Which artifacts it accepts (Type + State requirements)
- Output: What artifact it produces
- Acceptance: Under what conditions the output is considered successful

### Artifact Dependency Rules
- Pipeline inputs MUST reference sealed artifacts, and MUST NOT reference unsealed intermediate states.
- Dependency relationships between artifacts MUST be explicitly declared, implicit dependencies are prohibited.
- The dependency graph MUST be a Directed Acyclic Graph (DAG), circular dependencies are prohibited.
- When an artifact is replaced, all downstream pipelines depending on it MUST be re-verified.

### Composition Patterns
- Series: A >> B (Output of A as Input of B)
- Parallel: A || B (Execute simultaneously, merge results)
- Conditional: cond ? A : B (Choose path by condition)
- Loop: A * n (Repeat execution, with limit)
- Aggregate: A + B → C (Merge multiple artifacts into one)

### Pipeline Boundary Principles (DB Layer vs App Layer)
- **Do in DB if possible**: Data transformation, aggregation, constraints, state machine transitions.
- **Must do in App**: External calls, File IO, AI inference, Human-Computer Interaction.
- **Hybrid Pipeline**: DB handles data, App handles side effects and external interactions.

**Decision Tree (Simplified)**:
```
External Call? Yes → App Layer
No → Pure Data Transformation? Yes → DB Layer
No → Complex Business/Requires Human? Yes → App Layer
No → DB Layer
```

**Transaction Boundaries**:
- DB transactions only contain DB operations; external calls must be outside the transaction.
- External failures must have compensation (Release inventory/Cancel order).

**Coordination Patterns**:
- Orchestration: App layer explicitly orchestrates steps.
- Choreography: DB triggers events, App layer listens and responds.
- Saga: Each step has compensation; execute compensation in reverse on failure.

### Composition Abstraction Mechanisms
- **Generics**: Reuse contracts with type parameters (CRUD<T, ID>).
- **Inheritance**: Common errors/middleware/headers defined in base class.
- **Templates**: Structure reuse (Pagination list, Batch processing).
- **Mixin**: Composition of cross-cutting capabilities like auditable/cacheable.

### Composition Safety Rules
- Type Compatibility MUST check: `A.output` type is assignable to `B.input`.
- Error Propagation MUST declare: Composition contract must cover all error cases of child contracts.
- Seal Constraint MUST propagate: Composition artifact's seal MUST contain `evidence_refs` of all input artifacts.

---

## Mechanism

### L1 · Lightweight

Pipeline = Manual Composition. No formal pipeline definition needed, but artifact dependency relationships must be recorded clearly.

**Dependency Management**:
- Record `depends_on` in artifact metadata (list of dependent artifact IDs).
- Manual confirmation of dependency correctness is sufficient.

```yaml
artifact:
  id: string
  depends_on: [string]   # List of dependent artifact IDs
  produced_by: string    # Which contract/task produced it
```

**Composition Method**: Manually specify input artifacts, manually verify output.

---

### L2 · Standard

Pipeline = Assembly unit with a contract, dependency relationships maintained by the system.

**Pipeline Definition**:
```yaml
pipeline:
  id: string
  name: string
  contract:
    inputs:
      - artifact_type: code_module
        state: sealed               # MUST be sealed
      - artifact_type: test_suite
        state: sealed
    output:
      artifact_type: integrated_module
    acceptance: string              # Acceptance criteria
    error_handling: string          # Error handling strategy
```

**Dependency Management**:
- System maintains artifact dependency graph (DAG).
- Auto-check before pipeline execution: Are all input artifacts sealed?
- When input artifact is replaced, system marks downstream pipelines as "pending revalidation".

**Impact Analysis**:
```
Artifact X replaced
  → Query Dependency Graph: Which pipelines' inputs contain X?
  → Mark output artifacts of these pipelines as stale
  → Recursively down: Who depends on these stale artifacts?
  → Until no more downstream
```

**Data Structure**:
```yaml
artifact:
  # ...L1 fields...
  state: sealed | stale            # stale = dependency changed, needs revalidation
  dependency_graph:
    upstream: [artifact_id]         # Who I depend on
    downstream: [artifact_id]       # Who depends on me
```

---

### L3 · Strict

Pipeline = Auditable automated assembly line, dependencies forced execution, auto-cascading.

**Pipeline Enhancement**:
- Pipeline execution MUST generate a complete audit log (Input Artifact IDs + Output Artifact ID + Gate Results + Timestamp).
- Composition artifact's seal MUST contain `seal_hash` of all input artifacts (Evidence chain propagation).
- Composition abstractions (Generics/Inheritance/Templates/Mixin) MUST land as explicit input/output and error declarations upon final instantiation.

**Dependency Management Enhancement**:
- When artifact is replaced, system automatically triggers downstream revalidation (Cascading Revalidation).
- Downstream artifacts failing revalidation automatically enter rework.
- Dependency graph changes MUST be recorded in audit logs.

**Parallel Orchestration**:
- Pipelines with no dependency relationships can execute in parallel (Auto-judged by scheduler based on DAG).
- Pipelines with dependency relationships execute strictly in topological order.

**Data Structure Increment**:
```yaml
pipeline_execution:
  pipeline_id: string
  inputs: [{artifact_id, seal_hash}]   # Input snapshot
  output: {artifact_id, seal_hash}     # Output snapshot
  gate_results: [evidence_ref]         # Gate evidence
  executed_at: datetime
  triggered_by: string                 # Manual | Cascading Revalidation | Schedule

artifact:
  # ...L2 fields...
  seal:
    seal_hash: string
    input_seal_hashes: [string]        # seal_hash of all input artifacts
    sealed_at: datetime
```

---

## Practice

### Quick Selection Guide
- **Few artifacts, simple dependencies** → L1, recording `depends_on` is enough.
- **Multi-person collaboration, clear dependencies between artifacts** → L2, system maintains dependency graph, auto-mark stale.
- **Critical system, need full audit chain** → L3, cascading revalidation + seal chain propagation + auto parallel orchestration.

### Dependency Management Core Principles
- **Only depend on sealed things**: Uncertain artifacts cannot be referenced; this is the foundation of quality.
- **Dependencies must be explicit**: "Who I depend on" is written clearly, not guessed.
- **Changes must propagate**: If upstream changes, downstream must know and re-verify.
