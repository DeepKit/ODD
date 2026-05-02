---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.02对象-Object-Model]
---

# Artifact Taxonomy

## Intent
Use types to turn "essay questions" into "fill-in-the-blanks."
Each task produces exactly one artifact — a clear type tells you what to deliver and how to test it.

## Specification

### Classification Principles
- Every artifact MUST have a clear type (artifact_type).
- The type determines the artifact's structure, required fields, and test strategy.
- Each task MUST produce exactly one artifact (atomicity).

---

## Mechanism

### L1 · Lightweight

**Free naming.** Artifact types are described in natural language.

Common type examples:
- `code` — Source code file
- `test` — Test file
- `doc` — Documentation
- `config` — Configuration file
- `sql` — Database script

No mandatory specification — just be consistent.

---

### L2 · Standard

**Controlled type table.** The project maintains a type table with templates for each type.

```yaml
artifact_types:
  pg_function:
    title_template: "Create function {name}"
    required_fields: [name, params, return_type]
    test_strategy: pgTAP
  python_module:
    title_template: "Implement module {name}"
    required_fields: [name, input_spec, output_spec]
    test_strategy: pytest
  api_endpoint:
    title_template: "Implement endpoint {method} {path}"
    required_fields: [method, path, request_schema, response_schema]
    test_strategy: integration_test
  document:
    title_template: "Write {name}"
    required_fields: [name, audience]
    test_strategy: review
```

**Auto-linked test strategy**: Once the type is determined, the test strategy is automatically populated — no manual specification needed each time.

---

### L3 · Strict

**Standard Library (database as source of truth)**: On top of the L2 type table, each type carries a complete standard library.

Standard library fields (recommended minimum set):
- input_spec_template / output_spec_template (structure templates)
- side_effects_template (side-effect templates)
- implicit_requirements (implicit requirements)
- common_knowledge (common knowledge base)
- adversarial_tests (adversarial test vectors)
- bug_patterns (historical error-prone patterns)
- best_practices (recommended practices)
- feature_tree_template (functional tree template)
- temporal_defaults (time-dimension defaults)
- test_strategy (default verification strategy)

```yaml
artifact_types:
  pg_function:
    # ...L2 fields...
    input_spec_template: { params: [], return_type: "" }
    output_spec_template: { success: {}, error: {} }
    side_effects_template: [db_write]
    implicit_requirements:
      - "Must handle NULL input"
    common_knowledge:
      - "Default transaction isolation level is read_committed"
    adversarial_tests:
      - "SQL injection"
    bug_patterns:
      - "Unclosed cursor"
    best_practices:
      - "Use parameterized queries"
    feature_tree_template:
      - "pg_function.validate_input"
    temporal_defaults:
      lifecycle: medium_term
      data_growth: linear
      concurrency: 10-100
    test_strategy: pgTAP
```

**Knowledge injection flow**:
1. Identify artifact_type → load standard library.
2. implicit_requirements → inject into contract acceptance criteria.
3. common_knowledge / best_practices → inject into context and generation constraints.
4. adversarial_tests / bug_patterns → inject into adversarial and test strategies.
5. temporal_defaults → fill temporal_config (one-click confirmation).

---

## Practice

### Quick Selection
- **Small projects** → L1: free naming, just be consistent.
- **Team projects** → L2: maintain a type table with auto-linked test strategies.
- **Critical systems** → L3: standard library + automatic knowledge injection.

### Core Principles
- **One task, one artifact**: Atomicity is the foundation of the honeycomb.
- **Type determines template**: Once the type is clear, what to deliver and how to test are both determined.
