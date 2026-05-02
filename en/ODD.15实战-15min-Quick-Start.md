---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.00入门-3min-Guide, ODD.01总览-Overview]
---

# 15-Minute Quick Start Guide

## Intent
After reading the 3-minute guide and overview, you understand ODD concepts — but concept is not capability.
This document uses two hands-on exercises to help you complete the leap from knowing to doing in 15 minutes.

## Specification
- Exercise 1 (10 minutes): Individual developer, complete a full sealing workflow for one artifact.
- Exercise 2 (+5 minutes): Small team collaboration, experience contract adversarial and cross verification.
- All YAML can be copied and used directly, no extra tools required.

## Mechanism

---

### Exercise 1: 10 Minutes — Your First Sealed Artifact

**Scenario**: You will write a `format_date` function that formats `2026-01-10` as `January 10, 2026`.

#### Step 1: Write the Contract (2 minutes)

Copy the YAML below and fill in your project info:

```yaml
contract:
  id: C-001
  title: "Date Formatting Function"
  scope_in: "Convert ISO date string to human-readable English format"
  scope_out: "No time handling, no timezone"
  acceptance_criteria:
    - given: "Valid date 2026-01-10"
      when: "Call format_date('2026-01-10')"
      then: "Return 'January 10, 2026'"
    - given: "Valid date 2025-12-25"
      when: "Call format_date('2025-12-25')"
      then: "Return 'December 25, 2025'"
    - given: "Invalid input 'not-a-date'"
      when: "Call format_date('not-a-date')"
      then: "Raise ValueError, message contains 'invalid date'"
    - given: "Empty string"
      when: "Call format_date('')"
      then: "Raise ValueError"
  boundary_cases:
    - "Leap day 2024-02-29 → February 29, 2024"
    - "No leading zeros for month/day: January, not 01"
  floor: "All acceptance_criteria must pass"
  red_line: "Must not modify input parameters"
  human_confirmed: true
```

**Checkpoint**: Your contract has 4 acceptance criteria + 2 boundary cases + floor + red line. This is L2 standard.

#### Step 2: Create the Task (1 minute)

```yaml
task:
  id: T-001
  title: "Implement format_date"
  contract_id: C-001
  artifact_type: "function"
  artifact_name: "format_date"
  artifact_path: "src/utils/date.py"
  input_spec: "date_str: str (ISO format)"
  output_spec: "str (English date) or ValueError"
  acceptance_criteria:
    - "Pass all acceptance criteria of contract C-001"
  error_cases:
    - "Invalid format → ValueError"
    - "Empty string → ValueError"
  depends_on: []
  task_level: L1
```

#### Step 3: Execute + Verify (5 minutes)

Write the code (or have AI write it), then verify using input-output mappings in the contract:

```
Input: format_date("2026-01-10")  → Expected: "January 10, 2026"   ✅/❌
Input: format_date("2025-12-25")  → Expected: "December 25, 2025"  ✅/❌
Input: format_date("not-a-date")  → Expected: ValueError           ✅/❌
Input: format_date("")            → Expected: ValueError           ✅/❌
Input: format_date("2024-02-29")  → Expected: "February 29, 2024"  ✅/❌
```

All ✅ → proceed to sealing. Any ❌ → rework, fix and verify again.

#### Step 4: Seal (2 minutes)

```yaml
evidence:
  evidence_type: "output_verification"
  gate: "quality_check"
  result: pass
  summary: "5/5 input-output mappings passed"
  contract_id: C-001
  task_id: T-001

seal:
  artifact_version: "1.0.0"
  evidence_bundle: ["evidence-T-001-quality_check"]
  sealed_at: "2026-02-11T15:00:00Z"
  sealed_by: "your_name"
```

**Done!** You just completed the ODD core loop: **Contract → Execute → Verify → Seal**.

---

### Exercise 2: +5 Minutes — Full Team Collaboration Flow

**Scenario**: Based on Exercise 1, you need a `format_date_range` function to format two dates into a range.

#### Step 1: Write Contract Draft (1 minute)

```yaml
contract:
  id: C-002
  title: "Date Range Formatting"
  scope_in: "Convert two ISO dates to English range representation"
  scope_out: "No cross-year abbreviation handling"
  acceptance_criteria:
    - given: "Normal range"
      when: "Call format_date_range('2026-01-01', '2026-01-31')"
      then: "Return 'January 1, 2026 — January 31, 2026'"
    - given: "Same day"
      when: "Call format_date_range('2026-01-01', '2026-01-01')"
      then: "Return 'January 1, 2026'"
    - given: "Start date later than end date"
      when: "Call format_date_range('2026-02-01', '2026-01-01')"
      then: "Raise ValueError, message contains 'start > end'"
  boundary_cases:
    - "Cross-year: 2025-12-31 to 2026-01-01"
  floor: "All acceptance_criteria must pass"
  red_line: "Must not modify input parameters; must reuse sealed format_date"
  depends_on: [C-001]
  human_confirmed: false        # ← Not confirmed yet, run adversarial first
```

#### Step 2: Clarity Assessment (1 minute)

Play the assessor role and check the contract:

```yaml
clarity_detect:
  overall: slightly_unclear
  score: 1
  action: suggest
  issues:
    - type: "missing_boundary"
      description: "Null input behavior not defined"
      severity: yellow
```

Found a 🟡 item: null input not defined. Add:

```yaml
    - given: "Null input"
      when: "Call format_date_range(null, '2026-01-01')"
      then: "Raise ValueError"
```

#### Step 3: Simple Adversarial (2 minutes)

Play the Challenger to attack the contract:

```
Challenger: "What if the two dates use different formats, e.g., '2026/01/01' and '2026-01-01'?"
→ Fix: scope_in clarifies "Both parameters are ISO 8601 format (YYYY-MM-DD)"

Challenger: "What if the dependent format_date is not sealed?"
→ Answer: It is sealed (Exercise 1 completed), depends_on: [C-001] points to sealed version.

Attacker: "I can return a hardcoded string to pass tests."
→ Fix: Add property validation on random date pairs — result MUST include both input dates formatted.
```

Record adversarial evidence:
```yaml
pk_history:
  - round: 1
    attacker: Challenger
    attack_vector: boundary
    issue: "Input format not restricted"
    fix: "scope_in adds ISO 8601 constraint"
    verdict: pass
  - round: 2
    attacker: Attacker
    attack_vector: malicious
    issue: "Can hardcode to pass"
    fix: "Add property validation"
    verdict: pass
```

Change `human_confirmed` to `true`.

#### Step 4: Execute + Seal (1 minute)

Reuse the flow from Exercise 1: write code → input-output verification → seal.

```yaml
seal:
  artifact_version: "1.0.0"
  evidence_bundle:
    - "evidence-T-002-quality_check"
    - "evidence-T-002-pk_history"
  sealed_at: "2026-02-11T15:10:00Z"
  sealed_by: "your_name"
  input_seal_hashes:
    - "seal-C-001-v1.0.0"      # Depends on Exercise 1 sealing
```

**Done!** You experienced: contract dependency, clarity assessment, adversarial generation, evidence sedimentation — this is the L2 team collaboration flow.

---

## Practice

### Next Steps
- Deepen contract design → `ODD.06对抗-Contract-Adversarial.md`
- Understand state flow → `ODD.03状态-State-Machine.md`
- Use more templates → `ODD.0A模板-Template-Library.md`
- Understand verification principles → `ODD.10验证-Native-Verification.md`

### Core Principles
- **Agree before doing**: No contract, no direction; no acceptance criteria, no definition of done.
- **Seal in small steps**: One function, one seal. Do not wait until everything is done to verify.
- **Adversarial is not nitpicking**: It finds issues before execution; cost is far lower than rework.
- **Dependencies must be sealed**: If upstream is not sealed, downstream cannot start — basic pipeline discipline.
