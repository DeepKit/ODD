---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.07产物-Artifact-Taxonomy]
---

# Bug Map and Best Practices

## Intent
The Functional Tree tells you "what to do", the Bug Map tells you "what pitfalls to avoid", and Best Practices tell you "how to do it best".
Together they are called the **Three Magic Tools** (Functional Tree + Bug Map + Best Practices), automatically injecting context during contract generation and code generation phases, turning implicit knowledge into explicit constraints.

## Specification

### Three Magic Tools Principles
- Each artifact type (`artifact_type`) SHOULD be associated with its own Bug Map and Best Practices.
- The content of the Three Magic Tools MUST be injected into Contract and Task contexts as implicit requirements (see `ODD.05上下文-Context-Engineering.md`).
- Bug Maps and Best Practices SHOULD be continuously learned and updated from execution history, not static configurations.

### Injection Timing
- **Contract Generation Phase**: Bug Map → Acceptance Criteria Supplement; Best Practices → Contract Constraint Guidance.
- **Code Generation Phase**: Bug Map → Adversarial Test Vectors; Best Practices → Code Generation Guidance.
- **Test Phase**: Bug Map → Experience Library Attack (Sorted by historical frequency).

---

## Mechanism

### L1 · Lightweight

**Manually Maintained.** Record common pitfalls and recommended practices in project documents or notes, manually browse before development.

Common Pitfalls List Example:
- Password stored in plain text
- NULL input not handled
- Concurrency conflicts not considered
- Error messages leak internal details

Recommended Practices List Example:
- Encrypt passwords with bcrypt/argon2
- Validate boundaries for all inputs
- Protect database operations with transactions
- Standardize error messages, do not expose stack traces

No auto-injection, rely on human memory and discipline.

---

### L2 · Standard

**Structured Storage + Auto-Injection by Type.**

#### Bug Map

Maintain a Bug Map (Bug Intention Map) for each artifact type, recording historical error-prone patterns for that type.

Structure:
```yaml
bug_patterns:
  - id: BP-001
    pattern: "Password stored in plain text"            # Pattern Name
    detection_rule: "stored_password == hash(input_password, salt)"  # Formal detection rule
    severity: critical                  # Severity: critical / high / medium / low
    frequency: 127                      # Historical occurrence count
    prevention: "Use bcrypt or argon2"  # Preventive measure
  - id: BP-002
    pattern: "No login failure count"
    detection_rule: "login_attempts >= 5 IMPLIES account_locked == true"
    severity: high
    frequency: 89
    prevention: "Implement failure counting + account locking"
```

Injection Method: When creating a task, the system queries the corresponding `bug_patterns` based on `artifact_type` and automatically injects them into the task context's "Adversarial Test" and "Acceptance Criteria".

#### Best Practices

Maintain a set of Best Practices for each artifact type.

Structure:
```yaml
best_practices:
  - id: PR-001
    practice: "Use parameterized queries"          # Recommended practice
    rationale: "Prevent SQL injection"             # Rationale
    anti_pattern: "String concatenation SQL"       # Corresponding anti-pattern
    priority: 9                                    # Priority 1-10
    is_mandatory: true                             # Is mandatory
  - id: PR-002
    practice: "SECURITY DEFINER needs fixed search_path"
    rationale: "Prevent search path injection attacks"
    anti_pattern: "Omit search_path setting"
    priority: 8
    is_mandatory: true
```

Injection Method: Before code generation, the system queries corresponding `best_practices`. `is_mandatory: true` ones are forced injected, others injected sorted by priority (trimmed by token budget).

#### Artifact Type Standard Example

Associate the Three Magic Tools with artifact types (see `ODD.07产物-Artifact-Taxonomy.md` L3):

```yaml
artifact_types:
  auth_login:
    # Functional Tree Template (See ODD.0B功树-Functional-Tree)
    feature_tree_template:
      - auth_login.validate_input
      - auth_login.check_credentials
      - auth_login.generate_token
      - auth_login.record_audit
      - auth_login.handle_failure

    # Bug Map
    bug_patterns:
      - {pattern: "Password stored in plain text", severity: critical, frequency: 127}
      - {pattern: "No login failure count", severity: high, frequency: 89}
      - {pattern: "Token no expiration time", severity: high, frequency: 76}
      - {pattern: "Error message leaks user existence", severity: medium, frequency: 234}

    # Best Practices
    best_practices:
      - {practice: "bcrypt/argon2 encrypt password", rationale: "Resist rainbow tables", mandatory: true}
      - {practice: "Login failure response delay", rationale: "Prevent timing attacks", mandatory: false}
      - {practice: "Token use JWT or secure random number", rationale: "Prevent forgery", mandatory: true}

    # Implicit Requirements (Auto-injected into Contract Acceptance Criteria)
    implicit_requirements:
      - "Password MUST be encrypted stored"
      - "Prevent brute force attacks"
      - "Record login audit logs"
      - "Handle network timeouts"

  api_endpoint:
    feature_tree_template:
      - api.validate_request
      - api.authorize
      - api.execute_logic
      - api.format_response
      - api.handle_error

    bug_patterns:
      - {pattern: "SQL Injection", severity: critical, frequency: 312}
      - {pattern: "Input length/type not validated", severity: high, frequency: 267}
      - {pattern: "No Authentication/Authorization check", severity: critical, frequency: 198}
      - {pattern: "Error response leaks internal stack", severity: medium, frequency: 156}
      - {pattern: "No rate limit causes DDoS", severity: high, frequency: 91}
      - {pattern: "Return data not desensitized", severity: high, frequency: 134}

    best_practices:
      - {practice: "Parameterized queries", rationale: "Prevent SQL Injection", mandatory: true}
      - {practice: "Unified error response format {code, message, request_id}", rationale: "Traceable + No internal leak", mandatory: true}
      - {practice: "Request rate limiting", rationale: "Prevent abuse", mandatory: false}
      - {practice: "Response field allowlist (No undeclared fields)", rationale: "Prevent data leakage", mandatory: true}

    implicit_requirements:
      - "Input MUST validate type and range"
      - "Return unified error format"
      - "Record access logs"
      - "Handle timeout and service unavailability"

  db_migration:
    feature_tree_template:
      - migration.validate_schema
      - migration.apply_changes
      - migration.verify_data
      - migration.rollback

    bug_patterns:
      - {pattern: "No rollback script", severity: critical, frequency: 203}
      - {pattern: "Drop column without data backup", severity: critical, frequency: 87}
      - {pattern: "Migration order dependency exception", severity: high, frequency: 156}
      - {pattern: "Large table ALTER locks table causing downtime", severity: critical, frequency: 67}
      - {pattern: "NOT NULL new column no default value", severity: high, frequency: 189}
      - {pattern: "Missing index causes slow query", severity: medium, frequency: 245}

    best_practices:
      - {practice: "Every migration MUST pair with rollback script", rationale: "Recoverability", mandatory: true}
      - {practice: "Add column then drop column (Two-step migration)", rationale: "Avoid destructive change", mandatory: false}
      - {practice: "Large table use pt-online-schema-change / pg_repack", rationale: "Avoid table lock", mandatory: true}
      - {practice: "Backup affected tables before migration", rationale: "Data safety net", mandatory: true}

    implicit_requirements:
      - "MUST have rollback plan"
      - "MUST NOT execute during peak hours"
      - "Data integrity check before and after migration"
      - "Record migration duration and affected rows"

  config_file:
    feature_tree_template:
      - config.load
      - config.validate_schema
      - config.apply
      - config.hot_reload

    bug_patterns:
      - {pattern: "Key/Password hardcoded", severity: critical, frequency: 278}
      - {pattern: "No schema validation, spelling error silent fail", severity: high, frequency: 312}
      - {pattern: "Environment difference unhandled (dev/staging/prod mixed)", severity: high, frequency: 167}
      - {pattern: "Config change service not restarted (Cached old value)", severity: medium, frequency: 198}
      - {pattern: "Missing default value causes startup crash", severity: high, frequency: 145}

    best_practices:
      - {practice: "Sensitive info read from env/secrets manager", rationale: "Not in repo", mandatory: true}
      - {practice: "Config file MUST have JSON Schema / YAML Schema validation", rationale: "Early error discovery", mandatory: true}
      - {practice: "Each field has default or marked required", rationale: "Prevent missing crash", mandatory: false}
      - {practice: "Config change records audit log", rationale: "Traceable", mandatory: false}

    implicit_requirements:
      - "MUST NOT contain plain text keys"
      - "MUST have schema validation"
      - "Support multi-environment override"
      - "Mechanism description for effect after change"
```

---

### L3 · Strict

**Adds on top of L2: Auto-learning + Dual-stream Sedimentation + Metrics Loop.**

#### Bug Map Learning Loop

Bug Maps are not static configurations but continuously learned from execution history:

```
Rework occurs → Extract failure reason → Match existing pattern?
  ├── Yes → frequency +1, update severity
  └── No → Create new pattern, mark source_task_id
           ↓
New pattern accumulation → Reaches threshold → Promote to standard library pattern
           ↓
Next task of same type → Auto-inject new pattern → Prevent similar errors
```

Learning Sources:
- **Rework Records**: Auto-extract Bug patterns after task failure (Semantic memory sedimentation).
- **Adversarial Test Results**: Vectors where attack succeeded are auto-added to Bug Map.
- **Human Feedback**: Issues marked by humans during review.

#### Best Practice Learning Loop

```
Task successfully sealed → Extract code patterns → Assess reusability
  ├── High reusability → Create Best Practice item
  └── Low reusability → Store in Workshop Knowledge Base (Do not upgrade to standard)
```

#### Anti-Pattern Library

Corresponding to Best Practices, maintain a set of Anti-Patterns. Each anti-pattern SHOULD contain:

```yaml
anti_patterns:
  - id: AP-001
    name: "Ambiguous Contract Definition"
    symptoms:                           # Symptoms
      - "Contract has only one sentence description"
      - "No clear acceptance criteria"
      - "ES/NES mixed up"
    consequences:                       # Consequences
      - "AI generation not as expected"
      - "Repeated rework"
      - "Cannot seal"
    solutions:                          # Solutions
      - "Use contract templates"
      - "Mandatory acceptance criteria >= 3 boundary cases + 1 error case"
      - "Must pass CAP verification"
  - id: AP-002
    name: "Improper Workshop Isolation"
    symptoms:
      - "Workshops share DB connection"
      - "One workshop crash affects others"
    consequences:
      - "Failure propagation"
      - "Cannot warm start"
    solutions:
      - "Independent connection per workshop"
      - "Failure isolation mechanism"
  - id: AP-003
    name: "NES disguised as ES"
    symptoms:
      - "Use tools to detect 'code quality'"
      - "Metrics green but actual problems exist"
    consequences:
      - "False sense of security"
      - "Quality out of control"
    solutions:
      - "Clarify ES/NES boundaries"
      - "Tools only detect objectively determinable items"
      - "Manual review for NES items"
```

#### Metrics

**Process Metrics**:
- Contract Definition Time: Target < 2 days (From Draft to Ready)
- Rework Rate: Target < 10% (Verification Failures / Total Tasks)
- Sealing Time: Target < 1 week (From Ready to Sealed)
- Workshop Utilization: Target 70–90% (Active Workshops / Total Workshops)

**Outcome Metrics**:
- Production Defect Rate: Target < 5% (Production bugs / Function points)
- Technical Debt Growth: Target Linear (Maintenance cost ratio)
- Knowledge Reuse Rate: Target > 70% (Warm start reused knowledge ratio)
- Bug Map Hit Rate: Target > 60% (Prevented bugs / Actual found bugs)

---

## Practice

### Quick Selection
- **Small Project** → L1, Manually maintain lists of common pitfalls and recommendations.
- **Team Project** → L2, Structured storage + Auto-injection by `artifact_type`.
- **Critical System** → L3, Auto-learning + Anti-Pattern Library + Metrics Loop.

### Core Principles
- **History is Lesson**: Bug Maps are pitfalls others have stepped in; must inject into context to let executors bypass.
- **Practice is Shortcut**: Best Practices are verified paths; reuse is better than starting from scratch.
- **Three Magic Tools Synergy**: Functional Tree locates "Where", Bug Map prevents "Pitfalls", Best Practices guide "How" — none can be missing.
- **Learning Loop**: Static configuration will become obsolete; continuous learning from execution history is the long-term value.
