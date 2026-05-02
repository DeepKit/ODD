---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.02对象-Object-Model]
---

# Contract Adversarial Protocol (CAP)

## Intent
If the contract is poorly written, all subsequent work is in vain.
Before a contract takes effect, it must pass two gates: **Clarity Assessment** (finding ambiguities) and **Adversarial Generation** (finding loopholes and missing boundaries).

## Specification

### Common Contract Defects
- **Ambiguity**: How fast is "high performance"?
- **Incompleteness**: No consideration for concurrency, null values, or failure scenarios.
- **Malicious Compliance**: Satisfying the contract literally but violating the intent (AI is particularly good at this).

### Clarity Assessment Principles
- Draft contracts MUST pass Clarity Assessment before entering Adversarial Generation.
- Ambiguities MUST be graded: 🟢 Clear / 🟡 Slightly Unclear / 🔴 Very Unclear.
- 🔴 items MUST be answered by humans before proceeding; 🟡 items SHOULD be supplemented but can be ignored.
- Give humans **Multiple Choice Questions**, not Fill-in-the-Blank.

### Adversarial Principles
- Adversarial generation MUST be completed before the contract takes effect.
- The adversarial process MUST be recorded (`pk_history`) as part of the contract evidence.

### Boundary Declaration
Each contract SHOULD contain two types of boundary declarations:
- **Floor**: Minimum conditions the contract must satisfy; if missing, the system is unusable.
- **Red Line**: Constraints that must never be violated; touching them triggers immediate termination.

Floor and Red Line MUST be identified during the Clarity Assessment phase; boundaries involving security or data integrity MUST be marked as Red Lines.

### Attack Strategy Library
The adversarial party SHOULD initiate challenges from the following three angles:

**Logic Loopholes**:
- Is there a logical gap between preconditions and postconditions?
- Is there an input that makes it impossible to satisfy any postcondition?
- Are there contradictory constraints?

**Boundary Conditions**:
- Are behaviors defined for null values, empty strings, ultra-long strings, and special characters?
- Are behaviors defined for max values, min values, and overflow values?
- Are there clear constraints for concurrency, timeout, and idempotency?

**Malicious Implementation (Genie Effect)**:
- Can a "lazy" implementation be constructed—passing all acceptance criteria but being completely useless?
- Can a "dangerous" implementation be constructed—complying with the contract but causing data leakage?
- Can a "shell" implementation be constructed—returning hardcoded values to pass tests?

---

## Mechanism

### L1 · Lightweight

**Clarity**: Self-check. Go through a checklist after writing the contract:
- Are ambiguous words used ("large amount", "as soon as possible", "appropriate", "reasonable")?
- Are acceptance criteria testable (can specific test cases be written)?
- Are boundary cases covered (null values, max values, concurrency)?
- Is there a "literally compliant but wrong" implementation method?
- Are Floor and Red Line declared?

**Adversarial**: No formal CAP. Self-check is sufficient.

---

### L2 · Standard

**Clarity**: System automated assessment + Human confirmation.

Ambiguity Type Detection:
- **Vague Expression**: Hit ambiguity word list (Rule matching, low compute) -> Count 1 item.
- **Missing Boundary**: Input/output range, exception handling, idempotency/rollback undefined (AI analysis, medium compute) -> Count 1 item.
- **Missing Dependency**: Referencing unsealed contracts/undefined external interfaces/undefined table structures -> Count 1 item.
- **Logical Conflict**: Contradiction, Acceptance Criteria conflicts with Description (**Critical**) -> Count 2 items.
- **Security Ambiguity**: Permission/Password/Payment/Audit policy undefined (**Critical**) -> Count 2 items.

**Ambiguity Word List**:
```
Quantity: large amount, small amount, appropriate, enough, some
Degree: as soon as possible, try best, reasonable, moderate
Range: etc., and so on, related, other
Condition: when necessary, if needed, depending on situation
```

**Scoring Rules**:
- 🟢 Clear: 0 ambiguous items.
- 🟡 Slightly Unclear: 1-2 items and no critical items.
- 🔴 Very Unclear: >=3 items, or hit critical items (Logical Conflict/Security Ambiguity).

**Scoring Output Fields** (`clarity_detect`):
```yaml
clarity_detect:
  overall: clear | slightly_unclear | very_unclear
  score: 0-5                       # Cumulative ambiguity score
  action: pass | suggest | must_answer
  issues:
    - type: string                 # Ambiguity type
      description: string
      severity: green | yellow | red
```

🔴 items MUST be presented to humans as multiple-choice questions (AI recommends options + Custom fallback).

**Multiple Choice Design Principles**:
- Multiple choice first, fill-in-the-blank as fallback. Humans choose rather than define from scratch.
- Each question SHOULD contain 3 AI-recommended options + 1 "Other" custom option.
- AI flags recommended items based on context.

Option Generation Rules:
| Scenario | Option Source |
|---|---|
| Numeric | AI recommends 3 common values + Custom |
| Boolean | Yes / No / Depends |
| Handling | Reject / Allow / Warn / Custom |
| Business Logic | Extract possible options from conversation history |

**Adversarial**: Another person (or AI) reviews the contract, SHOULD initiate checks from the three angles of the Attack Strategy Library.

Review Result Record:
```yaml
clarity:
  overall: clear | slightly_unclear | very_unclear
  issues: [{type, description, severity}]
  human_answers: [{issue_id, choice}]
review:
  reviewer: string
  attack_vectors_checked: [logic | boundary | malicious]
  issues_found: [string]
  resolved: bool
```

---

### L3 · Strict

**Clarity**: Adds **Dual AI Adversarial Detection** on top of L2 — Two AIs (or same model with different prompts) find ambiguities separately, taking the stricter one; differences are appended as must-clarify items. Switch to different models for adversarial when critical items are hit.

**Adversarial: Full CAP (Contract Adversarial Protocol) — Multi-Role Adversarial Loop.**

**Roles** (Can map to military tent roles or assigned independently):
- **Proposer**: Translates human intent into draft contract, fixes based on attacks.
- **Challenger**: Attacks from Logic Loopholes and Boundary Conditions angles.
- **Attacker**: Attacks from Malicious Implementation angle — constructing literally compliant but intent-violating implementations.
- **Arbiter**: Judges whether attacks are valid, decides whether to continue PK or pass/escalate to human.

**Process**:
```
Human Intent → Proposer drafts V1
  ↓
Challenger + Attacker attack V1
  ↓
Loopholes exist? → Yes → Proposer fixes → V2 → Attack again (Loop)
  ↓ No
Arbiter Final Review → Pass → Human Confirmation
```
- MUST have a maximum number of rounds (Suggested 3 rounds).
- If not converged within limit, MUST escalate to human judgment, marking controversial points.

**Evidence Sedimentation**:
```yaml
pk_history:
  - round: 1
    attacker: Challenger
    attack_vector: boundary
    issue: "Undefined behavior under concurrency"
    fix: "Add concurrency boundary cases, define locking strategy"
    verdict: pass
  - round: 2
    attacker: Attacker
    attack_vector: malicious
    issue: "Can return empty data to 'pass' acceptance"
    fix: "Acceptance criteria adds minimum data volume requirement"
    verdict: pass
  - round: 3
    attacker: Challenger
    attack_vector: logic
    issue: "Logical gap between precondition and postcondition"
    fix: "Supplement intermediate state constraints"
    verdict: pass
```

`pk_history` participates in sealing and auditing as part of contract evidence.

---

### Full Adversarial Dialogue Examples

The following 3 examples show how CAP operates in different scenarios.

#### Example 1: User Registration API (Logic Loophole Attack)

**Human Intent**: "User registration interface, accepts email and password, creates account."

```
[Proposer] Draft Contract V1:
  title: User Registration
  acceptance_criteria:
    - given: Valid email and password
      when: POST /register {email, password}
      then: Return 201 + user_id
    - given: Email already registered
      when: POST /register {email, password}
      then: Return 409 Conflict
  floor: Can login after successful registration
  red_line: Password must not be stored in plain text

[Challenger] Attack (Logic Loophole):
  "There are no constraints on password strength. Users can register with empty password or '1'.
   This does not violate the contract, but violates security intent."

[Arbiter] Verdict: Attack valid. Password constraints are a security baseline.

[Proposer] Fix → V2:
  + boundary_cases:
    - "Password length < 8 → Return 400, prompt 'password too short'"
    - "Password length > 128 → Return 400, prompt 'password too long'"
  + acceptance_criteria:
    - given: Empty password
      when: POST /register {email, password: ""}
      then: Return 400

[Attacker] Attack (Malicious Implementation):
  "I can store passwords using MD5. Technically it's not 'plain text', but it's extremely insecure.
   Red line only says 'not plain text', doesn't say what algorithm."

[Arbiter] Verdict: Attack valid. Red line needs to be more precise.

[Proposer] Fix → V3:
  red_line: "Password MUST be stored using bcrypt/argon2/scrypt, MUST NOT use MD5/SHA1/SHA256"

[Arbiter] Final Review: V3 Pass. Submit for Human Confirmation.
```

`pk_history` Record:
```yaml
pk_history:
  - round: 1
    attacker: Challenger
    attack_vector: logic
    issue: "No password strength constraint, empty password allowed"
    fix: "Add password length validation 8-128 + empty password boundary"
    verdict: pass
  - round: 2
    attacker: Attacker
    attack_vector: malicious
    issue: "MD5 is not plain text but insecure, Red line imprecise"
    fix: "Red line explicitly MUST bcrypt/argon2/scrypt"
    verdict: pass
```

#### Example 2: Order Amount Calculation (Boundary Condition Attack)

**Human Intent**: "Calculate total order amount, including discount and tax."

```
[Proposer] Draft Contract V1:
  title: Order Amount Calculation
  acceptance_criteria:
    - given: Item 100, Discount 10%, Tax 13%
      when: calculate_total(100, 0.1, 0.13)
      then: Return 101.70
  floor: Result accurate to cent
  red_line: Amount must not be negative

[Challenger] Attack (Boundary Condition):
  "1. What if discount > 100%? Discount = 1.5 means paying the user?
   2. What if item price = 0?
   3. Floating point precision: 0.1 + 0.2 ≠ 0.3, how to handle?"

[Arbiter] Verdict: All three attacks valid.

[Proposer] Fix → V2:
  + boundary_cases:
    - "Discount range [0, 1.0], exceed → ValueError"
    - "Price = 0 → Return 0.00"
    - "Price < 0 → ValueError"
  + acceptance_criteria:
    - given: Floating point precision
      when: calculate_total(0.1, 0, 0)
      then: Return 0.10 (Decimal operation, not float)
  + Spec Supplement: "Internal use of Decimal type to avoid floating point errors"

[Attacker] Attack (Malicious Implementation):
  "I can return 0.00 for all amounts,
   because floor only says 'accurate to cent', 0.00 is accurate to cent."

[Arbiter] Verdict: Attack valid. Floor needs to link with acceptance criteria.

[Proposer] Fix → V3:
  floor: "All acceptance_criteria MUST pass + calculation result accurate to cent"

[Arbiter] Final Review: V3 Pass. Submit for Human Confirmation.
```

`pk_history` Record:
```yaml
pk_history:
  - round: 1
    attacker: Challenger
    attack_vector: boundary
    issue: "Discount range/Zero price/Floating point precision undefined"
    fix: "Limit discount [0,1.0], zero price return 0.00, use Decimal"
    verdict: pass
  - round: 2
    attacker: Attacker
    attack_vector: malicious
    issue: "Returning 0.00 for all satisfies floor 'accurate to cent'"
    fix: "Floor linked with acceptance_criteria"
    verdict: pass
```

#### Example 3: File Export (Genie Effect Attack)

**Human Intent**: "Export user list as CSV file."

```
[Proposer] Draft Contract V1:
  title: User List CSV Export
  acceptance_criteria:
    - given: 3 users
      when: export_csv(users)
      then: Generate CSV file with 3 rows of data
    - given: 0 users
      when: export_csv([])
      then: Generate CSV file with only header
  floor: File can be opened correctly by Excel
  red_line: Must not export password field

[Attacker] Attack (Genie Effect):
  "I can generate a 3-row CSV, each row just writing 'data,data,data'.
   Satisfies '3 rows of data', but content is meaningless."

[Arbiter] Verdict: Attack valid. Acceptance criteria checks row count but not content.

[Proposer] Fix → V2:
  acceptance_criteria Modified:
    - given: User [{name: "John", email: "z@test.com"}]
      when: export_csv(users)
      then: |
        CSV contains header row: name,email,created_at
        Data row contains: John,z@test.com,<TIMESTAMP>
  + boundary_cases:
    - "Username contains comma → Field wrapped in double quotes"
    - "Username contains double quotes → Double quotes escaped"
    - "10000 users → File size < 50MB, Time < 10s"

[Challenger] Attack (Logic Loophole):
  "What about CSV encoding? Chinese usernames will be garbled in Excel.
   UTF-8 BOM or GBK?"

[Arbiter] Verdict: Attack valid. Encoding is a classic CSV pitfall.

[Proposer] Fix → V3:
  + Spec Supplement: "Encoding MUST be UTF-8 with BOM (Excel compatible)"
  + acceptance_criteria:
    - given: Chinese username "张三"
      when: Open with Excel after export_csv
      then: Display "张三" instead of garbled text

[Arbiter] Final Review: V3 Pass. Submit for Human Confirmation.
```

`pk_history` Record:
```yaml
pk_history:
  - round: 1
    attacker: Attacker
    attack_vector: malicious
    issue: "Can generate meaningless data to satisfy row count"
    fix: "Acceptance criteria verifies specific field content"
    verdict: pass
  - round: 2
    attacker: Challenger
    attack_vector: boundary
    issue: "CSV encoding undefined, Chinese will be garbled"
    fix: "Enforce UTF-8 with BOM + Excel readability acceptance"
    verdict: pass
```

---

## Practice

### Quick Selection
- **Small Project** → L1, Self-check list + Declare Floor/Red Line.
- **Team Project** → L2, Clarity Assessment + Manual Review.
- **Critical System** → L3, Dual AI Clarity + Full CAP Adversarial Loop.

### Core Principles
- **Contract Quality Determines Everything**: If the contract is poor, all subsequent gates are meaningless.
- **Assess then Attack**: Clarity assessment removes ambiguity, adversarial removes loopholes; neither step can be skipped.
- **Multiple Choice over Fill-in-the-Blank**: Let humans choose rather than define from scratch, reducing cognitive load.
- **AI Needs Adversarial Most**: AI is good at "literal compliance", the Attack Strategy Library is the lowest cost way to intercept such issues.
- **Floor and Red Line Must Be Declared**: Floor missing = System unusable; Red Line touched = Immediate termination.
