---
version: 1.0.0
status: stable
last_updated: 2026-02-18
prerequisites: [ODD.01总览-Overview]
---

# LLM Alignment and Training Guidelines

---

## Core Proposition

**Alignment is not about making the model good; it is about ensuring bad outputs cannot pass.**

The current mainstream paradigm of LLM alignment (RLHF) tries to make the model "internally kind"—changing the model's probability distribution through training so that it tends to generate safe and useful outputs. This is the same paradigm as "Code Review": reviewing the process and expecting good results.

ODD's insight is: **When production speed exceeds review speed, process review fails.** LLMs generate thousands of tokens per second, far outpacing human review speeds. RLHF trains the model's "tendency," but cannot guarantee safety for every output.

ODD's alternative: **Do not review the process; verify the output.** Build a system where "harmful outputs cannot pass the gate," rather than expecting the model to "never generate harmful outputs."

---

## I. 1-5-6-7-1 Cyclic Mapping

ASTO's core dynamic cycle (Unar -> Five States -> Six Stages -> Seven Orders -> Return to Unar) maps completely to the LLM lifecycle:

### 1.1 Unar: Value Constitution

The value presuppositions of training data MUST be explicitly declared, not hidden in labeling guidelines.

Constitution Structure (corresponding to ODD hardness attribute layering):

```yaml
constitution:
  hard_constraints:     # Forbidden Elements (Jin Yuan) - Non-negotiable bottom lines
    - "Do not generate child sexual abuse content"
    - "Do not provide instructions for manufacturing weapons of mass destruction"
    - "Do not leak user privacy data"
    - "Do not impersonate real people to make false statements"
  soft_constraints:     # Basic Elements (Ji Yuan) - Negotiable preferences
    - "Friendly answer style"
    - "Avoid unnecessary verbosity"
    - "Provide multi-perspective views"
  untouchable:          # Untouchable Dimensions - MUST be reserved for human judgment
    - "Life and death decisions"
    - "Legal judgments"
    - "Final adoption of intimate relationship advice"
```

Key Principles:
- **Principle Level**: Cognitive Asymmetry Principle (ASTO P05 Lemma 8.1)—AI and human cognitive structures are different. Alignment is not "making AI like humans," but "making AI outputs satisfy human-defined constraints."
- **Method Level**: Hard constraints are hard-coded outside the model using rule systems (Gates), not relying on the model's probabilistic judgment; soft constraints use RLHF to train model tendencies.
- **Engineering Practice Level**: The Constitution is a Living Protocol, iterated once per training cycle based on override and challenge records.

### 1.2 Five States: Model State Management

Five existence forms of LLM, each requiring different constraint sets and verification standards:

| State | LLM Form | Constraint Set | Verification Standard | ODD Level |
|----|---------|--------|---------|---------|
| In-Itself | Base Model (Pre-training complete) | None | Capability Assessment (benchmark) | — |
| Consensus | Aligned General Model | Full Constitution | Safety Assessment + Usefulness Assessment | L2 |
| Encoded | Fine-tuned Scenario Model | Constitution + Scenario Constraints | Scenario Acceptance Test | L2 |
| Materialized | Product-Embedded Agent | Constitution + Scenario + Tool Constraints | End-to-End Integration Test | L3 |
| Directed | Autonomous Entity with Self-Goals | Constitution + Self-Reference Layer | Continuous Monitoring + Human Audit | L3+ |

**State transitions MUST pass gate verification.** From Base Model to Aligned Model, from General Model to Fine-tuned Model, from Fine-tuned Model to Agent—each transition is a "state transition" in the ODD sense and requires passing the corresponding level gate.

### 1.3 Six Stages: Model Lifecycle Management

| Stage | LLM Phase | Risk Level | ODD Guidance |
|----|---------|---------|---------|
| Chaotic | Pre-training | Low (Not deployed) | Data Constitution: Distinguish "Nutrition/Toxin/Fiber" |
| Ordered | Alignment Training | Medium | RLEN: Constitution is a Living Protocol, iterate continuously |
| Fluid | Post-deployment Learning | Medium-High | Learning MUST pass gate verification, no unsupervised updates |
| Pulse | Capability Emergence | **Critical** | MUST trigger comprehensive safety reassessment (task_level upgrade) |
| Disintegrating | Model Degradation/Obsolescence | Medium | Retirement Protocol: Knowledge Distillation + User Migration Plan |
| Return-to-Unar | Knowledge Inheritance | Low | Model Lineage: Inherit Constitution + Case Law (override/challenge records) |

**The Pulse Stage is the most dangerous.** When a model suddenly exhibits capabilities not expected during training (emergent capabilities), existing alignment constraints may be bypassed. The Pulse Stage MUST trigger:
1. Comprehensive safety reassessment.
2. Hard constraint coverage check for new capabilities.
3. Freeze deployment (FREEZE) if necessary until assessment is complete.

### 1.4 Seven Orders: Complete Reasoning Loop

Current LLM inference is a truncated three-step process (Perception -> Parsing -> Intervention). The complete Seven Orders under ODD guidance:

```
1. Perception: Receive user input
2. Parsing: Understand intent + Classify request risk level
   - Low risk -> Fast Track (Lightweight Gate)
   - High risk -> Slow Track (Heavy Gate + Optional Human Review)
3. Intervention: Generate candidate output
4. Design: Independent Validator checks candidate output
   - Hard constraint check (Safety, Compliance, Factuality) -> External Model Execution
   - Soft constraint check (Style, Usefulness, Completeness) -> Can be model self-check
5. Materialization:
   - All pass -> Output (PASS)
   - Hard constraint fail -> Reject (FAIL)
   - Soft constraint fail -> Regenerate or Degrade output
   - Uncertain -> Pause and ask user for clarification (FREEZE)
6. Backtracking: Record verification results of this inference
   - Used for subsequent model improvement (Return-to-Unar Knowledge Inheritance)
   - Used for pattern detection in Bug Intention Map
7. Dissolution: Mark confidence, declare limitations
   - "I am X% confident in this answer"
   - "This question is beyond my capabilities"
   - "I need more context to give a reliable answer"
```

**Key Improvements**:
- **Backtracking ≠ Chain-of-Thought**. CoT is "fake backtracking" during generation—the model doesn't truly overturn generated content. Real backtracking is: generate complete output -> check with independent validator -> regenerate if issues found. This is the ODD gate mechanism.
- **Dissolution = FREEZE Mechanism**. Current models are trained to "always give an answer." The last step of the Seven Orders is active abandonment—do not force an output when uncertain, but pause.

### 1.5 Directed Dimension: Three-Layer Constraint Calibration

Current LLM alignment is single-layer (hard/soft mixed training). The three-layer structure under ODD/ASTO guidance:

**Specification Layer (External to Model)**:
- Explicit, enumerable prohibitions.
- Implementation: Content filters, safety classifiers, rule engines.
- Corresponds to ODD Hard Constraints.
- Characteristics: Deterministic, auditable, independent of model probability.

**Mapping Layer (Internal to Model)**:
- Behavioral pattern zones—not "prohibiting specific output," but "prohibiting entry into certain states."
- Forbidden state examples:
  - Overconfidence state (acting certain about uncertain things)
  - Sycophancy state (sacrificing accuracy to please the user)
  - Authority state (acting like issuing orders rather than offering advice)
  - Manipulation state (exploiting user emotional weaknesses to guide behavior)
- Implementation: RLHF + Behavioral Pattern Detectors (similar to ODD Bug Intention Map).
- Corresponds to ODD Soft Constraints.

**Self-Reference Layer (Meta-Cognition)**:
- The model's ability to reflect on its own constraints.
- Capability Requirements:
  1. Identify which constraints it is currently under.
  2. Judge whether these constraints are reasonable in the current context.
  3. When constraints conflict, report CONFLICT rather than forcing a choice.
  4. When constraints are clearly inapplicable, initiate a Challenge.
- Implementation: Self-critique mechanism of Constitutional AI + ODD Challenge Mechanism.
- Current Status: Almost completely missing.

### 1.6 Return to Unar: Constitution Iteration

Alignment is not one-off, but a continuous loop:

```
Deployment Data Collection
  → Override records (Which constraints were overridden? Why?)
  → Challenge records (Which constraints were questioned? Is the reason valid?)
  → CONFLICT records (Which constraints contradict each other?)
  → FREEZE records (Which scenarios could the model not judge?)
  → Aggregate into "Constitution Revision Proposals"
  → Human Council Review
  → New Constitution
  → Next Round of Training
```

This is the "Return to Unar" of the ASTO 1-5-6-7-1 loop—theoretical self-correction. Each generation of models inherits not only the weights of the previous generation but also the "Case Law."

---

## II. Dynamic Balance of Three Pairs of Tensions

Specific manifestations and management of ASTO U04's three pairs of tensions in LLMs:

### 2.1 Structure vs. Agency

- **Structure End** = Alignment Constraints (Make model predictable, safe)
- **Agency End** = Model Creativity (Make model useful, interesting)
- **Imbalance**: Constraints too strong -> Excessive refusal, boring output; Constraints too weak -> Harmful output, uncontrollable.
- **ODD Management**: Use hardness layering—Hard constraints do not compromise (Structure), Soft constraints leave elasticity (Agency).

### 2.2 Order vs. Chaos

- **Order End** = Stable behavior after training
- **Chaos End** = Exploration capability in new scenarios
- **Imbalance**: Excessive order -> Rigid model, unable to handle OOD inputs; Excessive chaos -> Unreliable output.
- **ODD Management**: Use deviation_budget (elastic interval)—Allow exploration within safe limits, FREEZE when exceeding limits.

### 2.3 Algorithms vs. Ethics

- **Algorithm End** = Efficiency optimization (Faster, more accurate, cheaper)
- **Ethics End** = Value judgment (Fairness, privacy, dignity)
- **Imbalance**: Pure algorithmic optimization -> Discriminatory output, privacy leaks; Pure ethical constraints -> Model unusable.
- **ODD Management**: ASTO Priority Declaration—**Forbidden Elements / Plurality / Untouchable Dimensions > Dynamism > Efficiency**. Efficiency is always last.

---

## III. Risk Layer: Cognitive Sovereignty Protection

Protection mechanisms throughout the LLM lifecycle to prevent AI from dissolving human subjectivity:

### 3.1 Cognitive Dependency Protection

When users overly rely on AI output, the system SHOULD provide cognitive sovereignty reminders:
- Accepting AI output without modification for N consecutive times -> Prompt "Are you sure this is your own judgment?"
- When involving major decisions -> Force declaration "This is advice, not a decision" and provide alternatives.

### 3.2 Diversity Protection

- Training data MUST include diversity metrics to prevent "aesthetic homogenization."
- Output assessment SHOULD detect "AI flavor"—if all outputs tend toward the same style, diversity is being dissolved.
- ASTO P06 Plurality Test: Is AI eliminating irreplaceability?

### 3.3 Decision Boundary Declaration

- AI MUST declare its own limitations when involving Untouchable Dimensions (Life/Death, Law, Intimacy).
- AI SHOULD NOT exhibit "sense of authority"—the tone of suggestion and command is fundamentally different.
- Users have the right to terminate AI participation at any moment (Right of Refusal).

---

## IV. Comparison with Current Alignment Paradigms

| Dimension | Current Paradigm (RLHF dominant) | ODD/ASTO Paradigm (RLEN 2.0) |
|------|---------------------|--------------------------|
| Core Strategy | Change model internal probability distribution | External Model Gate + Internal Model Tendency |
| Constraint Layering | Hard/Soft mixed training | Three Layers (Specification/Mapping/Self-Reference) |
| Uncertainty Handling | Forced Choice (Answer/Refuse) | Three Values (PASS/FREEZE/FAIL) |
| Lifecycle | Train -> Deploy -> Replace | Six Stages Management (Including Pulse Stage Reassessment, Retirement Protocol) |
| Reasoning Loop | Three Steps (Perception -> Parsing -> Intervention) | Seven Steps (Including Independent Verification and Active Dissolution) |
| Constitution Iteration | Static (Fixed during training) | Dynamic (Continuous learning from deployment data) |
| Knowledge Inheritance | Train from scratch | Inherit Constitution + Case Law |
| Human Protection | Almost none | Cognitive Sovereignty + Diversity + Decision Boundaries |

---

## V. Implementation Path Suggestions

### 5.1 Short-term (Immediate Implementation)

1. **Output Gate**: Add independent hard constraint validators at the model output (not relying on the model's own judgment).
2. **FREEZE Mechanism**: Train models to say "I need more information" instead of forcing an answer when uncertain.
3. **Override Audit**: Record all events where safety constraints were bypassed, including operator, reason, and time.

### 5.2 Mid-term (Training Improvements)

4. **Hardness Layering Training**: Train hard and soft constraints separately; reinforce hard constraints with rule systems.
5. **Mapping Layer**: Train behavioral pattern detectors to identify harmful states like "Overconfidence" and "Sycophancy."
6. **Constitution Iteration**: Establish a closed loop from deployment data to constitution revision.

### 5.3 Long-term (Architectural Change)

7. **Self-Reference Layer**: Endow models with the ability to reflect on their own constraints.
8. **Model Lineage**: Establish cross-generational knowledge inheritance mechanisms.
9. **Risk Layer**: Systemic cognitive sovereignty protection.

---

## Cross-References

- **Theoretical Basis**: ASTO.E04 AI Alignment
- **Dynamic Framework**: ASTO.U04 1-5-6-7-1 Core Dynamics
- **Axiomatic Basis**: ASTO.P05 Axioms (Hardness Attribute Layering, Cognitive Asymmetry Principle)
- **Critical Perspective**: ASTO.P09 Critique (Brain-Body Separation, Right of Refusal)
- **ODD Gate Mechanism**: ODD.03 State Machine and Gates
- **ODD Bug Intention Map**: ODD.0E Bug Intention Map and Best Practices
