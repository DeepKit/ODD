---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.00入门-3min-Guide]
---

# Overview

## Intent
ODD (Output-Driven Development) is an engineering methodology.

Core insight: **Code is a liability; outcomes are assets.** Only outcomes that have been contracted, verified, and sealed are trustworthy, reusable assets.

Core loop: **Contract → Execute → Verify → Seal.**

Core structure: **Honeycomb development.** Atomic artifacts combine through pipelines into new artifacts, forming a living network managed by a functional tree. Each cell is independently sealed, can be built in parallel, and the whole grows naturally.

Goal: Make "bad output unable to pass," rather than hoping "producers are smart enough."

> Traditional development assumes "trustworthy process → trustworthy result." ODD reverses this: "verifiable result → process need not be trusted." This is a paradigm shift from readability governance to verifiability governance.

## Specification

### Five Pillars
1. **Contract**: Defines "what to do and what counts as done."
2. **Artifact**: A verifiable, concrete deliverable.
3. **Gate**: A checkpoint for state transitions — substandard work doesn't pass.
4. **Evidence**: A verifiable record of gate checks.
5. **Seal**: Artifact + evidence locked and archived — tamper-proof.

### Structural Pillars
- **Functional Tree**: Business function index — locates artifacts, traces dependencies, analyzes impact.
- **Dependency Graph**: A DAG between artifacts — explicitly records who depends on whom.
- **Pipeline**: A contract-governed assembly line that combines sealed artifacts into new artifacts.

### Specification Language
- MUST: Required
- SHOULD: Recommended
- MAY: Optional

### Complexity Levels
All mechanism documents describe five complexity levels:
- **L0 · Compatible**: Existing projects / painless onboarding.
- **L1 · Lightweight**: Individual / small projects / prototypes.
- **L1.5 · Personal+AI**: Individual with AI assistance / local auto-verification.
- **L2 · Standard**: Team collaboration / moderate complexity.
- **L3 · Strict**: Critical systems / AI multi-role collaboration.

Start at L0 or L1, upgrade as needed. Different modules in the same project can use different levels.

### Core Paradigm: AI Is Untrusted, Test Results Are Trusted

ODD doesn't try to make AI write "good code" — it builds a system where "bad code" cannot pass.

| Old Thinking | New Thinking (TD-AI) |
|---|---|
| Optimize AI input, hope for good output | Verify AI output, ignore process |
| AI writes code, then writes tests | Define tests first, AI fills in |
| Tests are secondary | Tests define quality |
| Failure → upgrade model | Failure → check tests |

See `ODD.10验证-Native-Verification.md` for details.

---

### Contract Degradation Warning

CAP prevents contracts from being gamed, but not from being wrong. If the team's business understanding is flawed, contracts will faithfully formalize that misunderstanding — every gate passes, every artifact is sealed, yet the product delivers zero value. ODD guarantees "artifacts satisfy contracts," not "contracts satisfy reality." The latter is human responsibility. Three defenses: CAP adversarial attack on contract ambiguity, Challenge mechanism for anyone to question contracts, and periodic Seal audit against real-world outcomes.

---

## Mechanism Overview

### L1 · Lightweight
Minimal viable set — one person can run it.
- Contract = acceptance criteria + boundary cases.
- State machine = 4 states (pending → in_progress → review → done).
- Gate = automated tests pass.
- Evidence = test report.
- Seal = artifact archived.
- Dependencies = manually recorded depends_on.

### L2 · Standard
Team standard workflow.
- Contracts add quality scoring and semantic checks.
- State machine adds blocked, quality_check, acceptance, and rework loops.
- Gate = automated check + human review (two gates).
- Evidence = structured records + audit log.
- Seal = artifact + evidence bundle bound together.
- Dependencies = system-maintained DAG, auto-marks stale.
- Context = functional tree queries + token control.

### L3 · Strict
Critical systems / AI multi-role collaboration — the full system.
- Contracts go through adversarial generation (CAP).
- State machine dynamically inserts gate chains by risk level (mutation testing, adversarial testing, cross-review, human review).
- Evidence = immutable audit + evidence chain propagation.
- Seal = seal_hash binds all evidence_ref — state is irreversible.
- Dependencies = cascading re-verification + automatic parallel orchestration.
- Context = multi-layer injection + workshop knowledge base + dual-stream memory.
- Workshop model = parallel execution, resource isolation, fault recovery, cross-review.

---

## Practice

Reading order and complete document list: see `ODD.00索引-Index.md`.

### Scope of This Document Set
- Describes only engineering-executable objects, processes, gates, evidence, auditing, and context engineering.
- Does not discuss philosophy, ideology, or metaphysical narratives.

> ODD's design principles originate from an upstream theoretical interface about structure, responsibility, and human adjudication. This document set focuses on engineering practice; for philosophical foundations, use the current root README and upstream interface notes rather than treating this overview as a stand-alone theory source.

> For repository-level evidence claims, metrics, or empirical status, refer to `../../ODD.P99.4.案例、指标与实证证据索引.md` rather than treating this overview as the citation source.
