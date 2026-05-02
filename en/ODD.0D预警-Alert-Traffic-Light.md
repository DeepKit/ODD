---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.03状态-State-Machine, ODD.0F车间-Workshop-Model]
---

# Tiered Alerts and Traffic Lights

## Intent
The system produces signals during runtime — task rework, test failures, gate blocking.
The question is: which signals need human attention, and which can be handled automatically?
Tiered alerts answer this: use lamp states so humans can see the global situation at a glance, and use escalation rules to auto-handle what can be auto-handled, only interrupting humans when truly necessary.

## Specification

### Lamp State Definitions
All monitorable stages MUST use unified lamp states:
- **White**: Not reached this stage yet.
- **Green Blink** (breathing blink): In progress, normal.
- **Red Blink** (breathing blink): In progress but with issues, needs human attention.
- **Green Solid**: Stage completed.

### Alert Grading Principles
- The system MUST respond by severity, and MUST NOT alert everything.
- Low-level alerts MUST be auto-handled, not disturb humans.
- Red light escalation MUST block the task, waiting for human decision.
- Human decisions MUST be presented as multiple-choice options to reduce cognitive load.

### Red Blink Triggers
Any stage encountering the following MUST switch to red blink:
- Blocked state.
- Rework count reaches alert threshold.
- Gate check fails.
- Mutation test score below threshold.

---

## Mechanism

### L1 · Lightweight
No formal lamp states. Task states (pending / in_progress / done / rework) are the signals.
After failure, humans decide whether to continue.

---

### L2 · Standard

**Lamp Visualization**: Each task's key stages display lamp states.

Stage-to-lamp mapping:
```
Ready → Developing → Quality Check → Acceptance → Sealing
 ○       ○            ○              ○           ○
```

Lamp color rules:
- Current stage = Green Blink (normal) or Red Blink (issue).
- Completed stages = Green Solid.
- Not reached stages = White.
- rework state = Red Blink in Developing column.

**Rework Alerts (4 levels)**:
- **Normal** (0-1): Green Blink, normal execution.
- **Yellow Alert** (2): Log, diagnose failure reason. No human interruption.
- **Orange Alert** (4): Notify humans, but do not block task.
- **Red Escalation** (≥6): Block task, wait for human decision.

**Mutation Test Alerts (3 levels)**:
- **Normal** (first time < threshold): Auto rework to add tests.
- **Yellow Alert** (2 times < threshold): Log and continue attempts.
- **Red Escalation** (3 times < threshold): Block task, wait for human decision.

**Human Decision Menu** (provided when red light triggers):
- Modify contract description — contract unclear prevents correct implementation.
- Lower gate threshold — temporarily lower mutation test threshold.
- Manual assistance — human supplements key test cases or code snippets.
- Cancel task — abandon this task.
- Continue attempts — reset counters and continue despite warning.

---

### L3 · Strict

**Lamp Enhancement**: Add mutation testing, adversarial testing, and cross-review stages.

```
Ready → Developing → Quality Check → Mutation Test → Adversarial Test → Cross Review → Acceptance → Sealing
 ○       ○            ○              ○               ○                 ○             ○        ○
```

Red blink triggers per stage:
- **Ready**: blocked state (dependency blocked).
- **Developing**: rework_count ≥ 2 (warning); rework_count ≥ 6 (must human intervene).
- **Quality Check**: tests fail.
- **Mutation Test**: mutation_score < threshold.
- **Adversarial Test**: high-risk vulnerabilities found.
- **Cross Review**: reviewers reject pass.
- **Acceptance**: human acceptance rejects.

**Alert and Racing Linkage**:
- Yellow alert → trigger smart racing diagnosis (see `ODD.0C赛马-Smart-Racing.md`).
- Diagnosis = Executor Insufficient → auto-upgrade executor level.
- Diagnosis = Contract Ambiguous → trigger clarity re-assessment (see `ODD.06对抗-Contract-Adversarial.md`).
- Red escalation → block and freeze racing upgrades, wait for human decision.

**Data Structure**:
```yaml
task_warning:
  task_id: string
  current_stage: string
  lamp_state: white | green_blink | red_blink | green_solid
  warning_level: normal | yellow | orange | red
  rework_count: int
  mutation_attempts: int
  human_decision:
    decision: modify_contract | lower_threshold | manual_assist | cancel | retry
    decided_by: string
    decided_at: datetime
    note: string
```

**Audit**:
- All alert escalations MUST be recorded in audit logs.
- Human decisions MUST record selected option, decision maker, and time.
- Frequency and handling time of red escalations SHOULD be system health metrics.

---

## Practice

### Quick Selection
- **Small project** → L1, no lamp states, manual judgment.
- **Team project** → L2, lamp states + 4-level rework alerts + human decision menu.
- **AI multi-role collaboration** → L3, full-stage lamp states + alert/racing linkage + audit.

### Core Principles
- **Do not alert everything**: Low-level issues auto-handle, only disturb humans when necessary.
- **Lamp state is navigation**: A glance at global status; red blink = need you, green blink = no need.
- **Human decisions should be simple**: Provide multiple-choice menu, not open-ended analysis.
- **Alerts drive improvement**: High red alert frequency = poor contract quality or unreasonable task grading, needs systematic correction.
