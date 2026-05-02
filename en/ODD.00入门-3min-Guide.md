---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: []
---

# ODD: Output-Driven Development

## Intent
ODD (Output-Driven Development) is an engineering methodology.
Its core insight: **Code is a liability; outcomes are assets.**

Code requires maintenance, decays over time, and may contain errors — it is inherently a cost. Only outcomes that have been contracted, verified, and sealed are truly trustworthy and reusable assets.
ODD's goal is to shift development from "writing code" to "producing verifiable assets."

> Traditional development assumes "trustworthy process → trustworthy result": if the code is well-written and the review passes, the result must be fine. ODD reverses this: "verifiable result → process need not be trusted." This is a paradigm shift from readability governance to verifiability governance.

## Problems You May Have Encountered

- "What exactly should this requirement look like?" — Nobody can articulate it clearly; you only discover it's wrong after it's done.
- "Who tested this feature?" — Someone claims it was tested, but there's no record to be found.
- "A bug appeared in production, and no one knows which step caused it" — No traceability.
- "Code was silently modified without anyone knowing" — Outcomes have no protection.
- "AI-generated code quality is inconsistent, with no unified acceptance criteria" — Especially evident in human-AI collaboration.

## How ODD Solves This

- **Contract first**: Define acceptance criteria before starting work — no more "discovering it's wrong after finishing."
- **Evidence speaks**: Every check leaves a verifiable record — no relying on verbal promises.
- **Gate enforcement**: Substandard outcomes cannot proceed to the next step — problems are caught early.
- **Seal protection**: Verified outcomes are locked and archived — traceable and tamper-proof.
- **Human-AI universal**: Whether humans or AI produce the code, the same process and standards apply.

## Mechanism
ODD's minimal mechanism is "Contract → Execute → Verify → Seal."

## Four Actions

```
Contract → Execute → Verify → Seal
```

1. **Contract**: Before starting, clearly define "what to do and what counts as done." This is called a contract.
2. **Execute**: Work according to the contract, producing concrete deliverables (code, docs, configs…). These are called artifacts.
3. **Verify**: Check artifacts against the contract to see if they meet the standard. Checkpoints are called gates; check results are called evidence.
4. **Seal**: Lock and archive verified artifacts so they cannot be tampered with. This is called sealing.

## Specification
The minimal specification is three bottom lines — work cannot start/pass/seal without meeting them.

## Three Bottom Lines

- **No contract, no start**: If you don't know what to build, don't start building.
- **No evidence, no pass**: Saying "it's done" isn't enough — you need provable evidence.
- **No seal, no completion**: Verified work must be locked down to prevent silent modification.

## Practice
Start from L1, escalate by risk — no need to use the strictest process from the beginning.

## Complexity Is a Choice

Not every project needs the strictest process. ODD offers five levels — choose as needed:

- **L0 Compatible**: Existing projects. Use Git tags as seals, test reports as evidence.
- **L1 Lightweight**: Solo developer building small tools. Manual contracts, manual verification, manual sealing.
- **L1.5 Personal+AI**: Solo developer with AI assistance. AI generates contracts + tests, local auto-verification, local hash sealing.
- **L2 Standard**: Team collaboration. YAML contracts, CI auto-verification.
- **L3 Strict**: Critical systems or AI collaboration. Adds formal specs, mutation testing, adversarial generation, and evidence chain auditing.

Start at L0 or L1, upgrade when needed.

## Honeycomb Development: ODD's Structural Advantage

Traditional development produces a pile of files whose relationships exist only in people's heads. ODD is different.

ODD's artifacts are atomic — each artifact is self-contained, verified, and the smallest possible unit, like individually sealed honeycomb cells.
These atomic artifacts combine through pipelines to produce new artifacts; new artifacts can continue combining, forming a living network structure.
The entire network is managed by a functional tree — you can precisely locate any artifact, trace its origin, dependencies, and change impact.

```
Atomic Artifact ──┐
                  ├─ Pipeline Composition ─→ New Artifact ──┐
Atomic Artifact ──┘                                        ├─ Pipeline ─→ Larger Artifact
                       Atomic Artifact ────────────────────┘
                             ↑
                    Functional Tree Management
```

Structural benefits:
- **Reusable**: Sealed artifacts can be directly referenced by other pipelines — no rework needed.
- **Replaceable**: If an artifact has issues, replacing it doesn't affect other sealed parts.
- **Traceable**: From any final artifact, trace down the functional tree to every atomic unit.
- **Growable**: New features = new composition pipelines, without breaking existing structure.

Production benefits:

Each artifact has clear contract boundaries, so different people (or AI) can build different cells simultaneously without interference.

```
Workshop A ──Contract:User Login── → Artifact A (Sealed) ──┐
Workshop B ──Contract:Permission──  → Artifact B (Sealed) ──├── Pipeline → Larger Artifact
Workshop C ──Contract:Audit Log──   → Artifact C (Sealed) ──┘
```

- **Parallelizable**: Multiple workshops operate simultaneously, each sealing their own artifacts independently.
- **Isolatable**: One workshop failing doesn't affect others; the contract returns to the queue for a new workshop.
- **Scalable**: Not enough capacity? Add workshops. Artifacts are standardized — more workshops means more capacity.
- **Cross-reviewable**: What Workshop A builds, Workshop B inspects — avoiding "checking your own work."

This is "honeycomb development" — each cell is independently sealed and fully verified; cells can be built simultaneously; cells connect through structure, and the whole grows naturally.

## Core Vocabulary

- **Contract**: A clear agreement about a piece of work, including acceptance criteria.
- **Artifact**: The concrete output of work — code files, API docs, test reports, etc.
- **Gate**: A checkpoint; artifacts must pass through gates to proceed to the next stage.
- **Evidence**: The recorded result of a gate check, proving whether an artifact meets the standard.
- **Seal**: Locking a verified artifact and its evidence so they cannot be modified.
- **Pipeline**: A contract-governed assembly line that combines sealed artifacts into new artifacts.
- **Functional Tree**: A business function index that manages the positioning, tracing, and impact analysis of the artifact network.
- **Workshop**: An isolated execution environment; one contract binds to one workshop, and multiple workshops can operate in parallel.

> ODD was not designed in a vacuum. Behind it is an upstream constraint framework about human-AI collaboration in the AI era. If you want to know why ODD is designed this way — why three-valued instead of two-valued, why FREEZE is a feature not a fault, why human adjudication authority is non-transferable — read the current ODD root README and upstream interface notes.

> For repository-level evidence claims, metrics, or empirical status, refer to `../../ODD.P99.4.案例、指标与实证证据索引.md` rather than treating this quick guide as the citation source.
