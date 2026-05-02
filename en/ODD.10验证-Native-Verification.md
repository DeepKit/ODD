---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.01总览-Overview]
---

# ODD Native Verification

## Intent
Do not trust the AI's process, only trust the verifiable results.
Code written by AI is untrusted, tests written by AI are also untrusted — but **Human-defined Input-Output Mappings** are trusted.
ODD Native Verification uses the input-output mappings in the contract to directly contrast AI output, without relying on AI-generated test code.

## Specification

### Core Paradigm Shift (TD-AI)
```
Old Thinking: How to make AI write good code? → Optimize Input
New Thinking: How to prevent bad code from passing? → Verify Output

Old Formula: High Quality Code = Good Context + Good Contract + Good Model
New Formula: High Quality Code = Good Tests + Code Passing Tests
  Where: Good Tests = Good Contract + Test Validity Verification
```

### Six Principles
1. **AI is untrusted, only test results are trusted** — Do not try to make AI write "good code", but build a system where "bad code" cannot pass.
2. **Tests must be defined by an independent source** — Acceptance criteria in the contract (Human defined) or AI tests that have passed validity verification.
3. **Code is disposable, tests are permanent** — Code can be rewritten, tests are the definition of quality.
4. **Small steps, frequent verification** — Test every function written, do not wait until the end.
5. **Failure is learning, not punishment** — Record reasons for every failure, accumulate experience (see `ODD.0E法宝-Bug-Map-Best-Practices.md`).
6. **Adversarial Verification** — Tests must be verified by "attacks"; tests that can be bypassed are invalid tests.

### AI Uncertainty Prevention Strategies
1. **Output Verification > Code Review** — Do not review AI code logic, verify AI code output.
2. **Contract as Test** — `examples` in the contract automatically become test cases.
3. **Small Task Principle** — Let AI generate a single function (50 lines), not an entire module (500 lines).
4. **Idempotent Retry** — Retry if AI generation fails; generate multiple times for the same contract, pick the version that passes tests.
5. **Isolate Uncertainty** — Deterministic boundaries (Contract definition + Test execution + Output verification) surround the uncertain AI code generation zone.
6. **Human Fallback** — If AI fails N retries, escalate to human.

---

## Mechanism

### L1 · Lightweight

**Manual Verification.** Manually check if AI-generated code meets expectations.

Manually run through verification after writing the contract:
- Given input X, is the actual output Y?
- Are there exceptions for boundary inputs?

No automation, rely on humans.

---

### L2 · Standard

**ODD Native Verification = Input-Output Mapping + System Auto Contrast.**

#### Verification Process
```
Human defines Input-Output Mapping in Contract
  ↓
AI generates code based on mapping
  ↓
System calls code using inputs from contract
  ↓
System contrasts actual output and expected output
  ├── Match → Pass (quality_check pass)
  └── Mismatch → Rework
```

#### Four Mapping Definition Methods

**Enumeration** (Small input space, discrete):
```yaml
examples:
  - input: {username: "test", password: "123456"}
    output: {success: true, token: "<UUID>"}
  - input: {username: "test", password: "wrong"}
    output: {success: false, error: "Wrong password"}
```

**Property** (Complex logic, verifies output properties rather than exact values):
```yaml
properties:
  - "Result of sort(arr) MUST be sorted"
  - "Length of sort(arr) result MUST == Original array length"
  - "Elements of sort(arr) result MUST be a permutation of original array"
```

**Example** (Pattern inferable):
```yaml
examples:
  - input: {date: "2026-01-10"}
    output: "January 10, 2026"
  - input: {date: "2025-12-25"}
    output: "December 25, 2025"
```

**Rule** (Clear mathematical relationship):
```yaml
rule: "add(a, b) == a + b"
test_cases:
  - {a: 1, b: 2, expected: 3}
  - {a: 0, b: 0, expected: 0}
  - {a: -1, b: 1, expected: 0}
```

#### Complete End-to-End Examples of Four Mapping Methods

Each example below shows the complete process from contract definition to verification execution.

**Example A: Enumeration —— User Permission Check**

```yaml
# 1. Define mapping in contract
contract:
  title: "Check if user has permission to access resource"
  examples:
    - input: {user_role: "admin", resource: "settings"}
      output: {allowed: true}
    - input: {user_role: "guest", resource: "settings"}
      output: {allowed: false, reason: "insufficient_permission"}
    - input: {user_role: "editor", resource: "posts"}
      output: {allowed: true}
    - input: {user_role: "editor", resource: "settings"}
      output: {allowed: false, reason: "insufficient_permission"}
    - input: {user_role: "", resource: "posts"}
      output: {allowed: false, reason: "invalid_role"}

# 2. System executes verification
verification_run:
  - call: check_access("admin", "settings")
    actual: {allowed: true}
    expected: {allowed: true}
    result: PASS
  - call: check_access("guest", "settings")
    actual: {allowed: false, reason: "insufficient_permission"}
    expected: {allowed: false, reason: "insufficient_permission"}
    result: PASS
  # ... Remaining 3 same logic
  summary: "5/5 PASS"
```

**Example B: Property —— List Deduplication**

```yaml
# 1. Define properties in contract
contract:
  title: "List deduplication function"
  properties:
    - "unique(arr) result contains no duplicate elements"
    - "unique(arr) result is a subset of original array"
    - "unique(arr) preserves order of first appearance"
    - "unique([]) == []"
    - "unique(arr) length <= original array length"

# 2. System generates random test cases and verifies properties
verification_run:
  test_cases_generated: 100        # Randomly generate 100 inputs
  properties_checked:
    - property: "No duplicate elements"
      method: "len(result) == len(set(result))"
      pass_count: 100
    - property: "Subset of original"
      method: "all(x in arr for x in result)"
      pass_count: 100
    - property: "Preserve order"
      method: "Compare index order in original array"
      pass_count: 100
    - property: "Empty array"
      method: "unique([]) == []"
      pass_count: 1
    - property: "Length constraint"
      method: "len(result) <= len(arr)"
      pass_count: 100
  summary: "5 properties x 100 cases = 500 checks, ALL PASS"
```

**Example C: Example —— Phone Number Masking**

```yaml
# 1. Use few examples to show pattern in contract
contract:
  title: "Phone number masking: replace middle 4 digits with ****"
  examples:
    - input: {phone: "13812345678"}
      output: "138****5678"
    - input: {phone: "19900001111"}
      output: "199****1111"
    - input: {phone: "12345"}          # Non-standard length
      output: {error: "invalid_phone"}

# 2. System infers pattern from examples and generates more cases
verification_run:
  inferred_rule: "phone[:3] + '****' + phone[7:]"
  contract_examples:
    - call: mask_phone("13812345678")
      actual: "138****5678"
      expected: "138****5678"
      result: PASS
    - call: mask_phone("19900001111")
      actual: "199****1111"
      expected: "199****1111"
      result: PASS
    - call: mask_phone("12345")
      actual: {error: "invalid_phone"}
      expected: {error: "invalid_phone"}
      result: PASS
  generated_examples:                  # Auto-supplemented by system
    - call: mask_phone("18688889999")
      actual: "186****9999"
      rule_check: PASS
    - call: mask_phone("01012345678")
      actual: {error: "invalid_phone"}
      rule_check: PASS
  summary: "3 Contract Examples + 2 Generated Examples = 5/5 PASS"
```

**Example D: Rule —— Discount Calculation**

```yaml
# 1. Define math rule in contract
contract:
  title: "Calculate discounted price"
  rule: "discount_price(price, rate) == round(price * (1 - rate), 2)"
  constraints:
    - "price >= 0"
    - "0 <= rate <= 1"
    - "Result accurate to cent (Decimal)"
  test_cases:
    - {price: 100.00, rate: 0.1, expected: 90.00}
    - {price: 100.00, rate: 0.0, expected: 100.00}
    - {price: 100.00, rate: 1.0, expected: 0.00}
    - {price: 0.01, rate: 0.5, expected: 0.01}   # round(0.005, 2)
    - {price: 99.99, rate: 0.15, expected: 84.99} # round(84.9915, 2)

# 2. System executes verification
verification_run:
  contract_cases:
    - call: discount_price(100.00, 0.1)
      actual: 90.00
      expected: 90.00
      result: PASS
    - call: discount_price(100.00, 0.0)
      actual: 100.00
      expected: 100.00
      result: PASS
    - call: discount_price(100.00, 1.0)
      actual: 0.00
      expected: 0.00
      result: PASS
    - call: discount_price(0.01, 0.5)
      actual: 0.01
      expected: 0.01
      result: PASS
    - call: discount_price(99.99, 0.15)
      actual: 84.99
      expected: 84.99
      result: PASS
  rule_fuzz:                           # Rule fuzzing
    random_cases: 200
    formula_check: "actual == round(price * (1 - rate), 2)"
    pass_count: 200
  summary: "5 Contract Cases + 200 Random Cases = 205/205 PASS"
```

#### Dynamic Value Matching
When output contains dynamic values like UUID, timestamp, exact match is not possible, pattern matching is required:

| Dynamic Value Type | Expected Output Syntax | Matching Method |
|---|---|---|
| UUID | `<UUID>` | Regex `^[0-9a-f]{8}-...` |
| Timestamp | `<TIMESTAMP>` | Execution time ±5 seconds |
| Auto-Inc ID | `<INT>` | Positive Integer |
| Random String | `<TOKEN:32>` | String of length 32 |
| Float | `<FLOAT:0.01>` | Error ≤ 0.01 |
| Fixed Value | Direct Value | Exact Match |

Expected Output Example:
```json
{
  "id": "<UUID>",
  "created_at": "<TIMESTAMP>",
  "token": "<TOKEN:64>",
  "score": "<FLOAT:0.001>",
  "name": "Fixed value direct contrast"
}
```

---

### L3 · Strict

**Adds on top of L2: Validator Self-Test + Mutation Testing + Adversarial Verification.**

#### Validator Self-Test
The ODD validator itself MUST have complete test coverage:

| Test Category | Requirement |
|---|---|
| Positive Test: Correct output should pass | 100% Coverage |
| Negative Test: Incorrect output should be rejected | 100% Coverage |
| Boundary Test: Null, extreme, special chars | ≥ 90% Coverage |
| Dynamic Value Test: UUID, timestamp, random | 100% Coverage |

#### Mutation Testing Verifies Test Validity
Passing tests does not mean tests are effective — Mutation testing verifies test quality:
```
Code Generation → Unit Test Pass → Mutation Test
  → Deliberately introduce bug in code (Mutant)
  → Check if test can discover it
  → Discovered = Test Effective (Mutant "Killed")
  → Not Discovered = Test Ineffective (Need to supplement tests)
  → Mutation Score = Killed / (Total - Equivalent) ≥ 80%
```

Six Mutation Operators:
| Operator | Example |
|---|---|
| Arithmetic Operator Replacement (AOR) | `+` → `-`, `*` → `/` |
| Relational Operator Replacement (ROR) | `>` → `>=`, `=` → `<>` |
| Logical Operator Replacement (LOR) | `and` → `or`, `not` → Delete |
| Constant Replacement (COR) | `0` → `1`, `True` → `False` |
| Statement Deletion (SDL) | Delete assignment, delete return |
| Condition Boundary (CBM) | `x > 0` → `x >= 0` |

#### Pipeline Testing Strategy (Supplement)

**Test Pyramid**:
- 70% Unit Tests (Single pipeline, transaction rollback isolation)
- 25% Integration Tests (Real DB + mock external dependencies)
- 5% E2E Tests (Full flow)

**Contract Driven Testing**:
- Auto-generate positive tests from `examples`.
- Generate boundary tests from `input/output` constraints.

**Transaction Rollback Isolation**:
```yaml
test_isolation:
  mode: transaction_rollback
  reason: "Auto rollback after test, avoid cleanup cost"
```

**External Dependency Mock & Compensation Verification**:
- External calls must be mocked, verify compensation logic (refund/release inventory).
- Failure paths and compensation paths must have tests.

**Isolation Strategy** (Choose by complexity):
- Transaction Isolation (Recommended)
- Schema Isolation (Parallel testing)
- Snapshot Restore (Complex scenarios)

#### Adversarial Verification
```
AI-A (Developer): Write code + Write tests
AI-B (Attacker): Try to write code that passes tests but has bugs

AI-B Passes? → Tests not strict enough → AI-A supplements tests
AI-B Fails? → Tests effective
```

#### Complete Quality Assurance Flow
```
[Stage 1: Test Definition] — Human/Contract
  ↓ Contract defines acceptance criteria + boundary conditions
[Stage 2: Code Generation] — AI
  ↓ AI generates code based on contract
[Stage 3: Output Verification] — System (quality_check)
  ↓ Call code with contract inputs, contrast output
[Stage 4: Integration Verification] — Other Workshops (acceptance)
  ↓ Multi-artifact composition + Boundary testing
[Stage 5: Mutation Testing] — System (mutation_test)
  ↓ Verify test validity ≥ 80%
[Stage 6: Adversarial Testing] — System (adversarial_test, L3+)
  ↓ Attack code to find vulnerabilities
[Stage 7: Cross Review] — Other Workshops (cross_review, L3)
  ↓ Multi-party review + Escalate disagreement to human
[Stage 8: Sealing] — Auto
```

---

## Practice

### Quick Selection
- **Small Project** → L1, Manual verification.
- **Team Project** → L2, ODD Native Verification + Dynamic Value Matching.
- **Critical System** → L3, Validator Self-Test + Mutation Testing + Adversarial Verification.

### Core Principles
- **Output Contrast > Test Code**: Don't write test code, contrast output directly using input-output mappings in contract.
- **Human Defines Standards, Machine Executes Verification**: Test standards come from contract (Human confirmed), not from AI.
- **Dynamic Value Inexact Match**: UUID, timestamps use pattern matching to avoid false positives.
- **Validator Needs Testing Too**: If the validator has bugs, nothing is trusted.
