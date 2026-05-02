---
version: 1.2.0
status: stable
last_updated: 2026-02-11
prerequisites: []
---

# ODD Document Index

## Intent
Provide an at-a-glance reading path and terminology index.

> Document type: ODD (Output-Driven Development) engineering methodology document set
> Structure: Flat — all documents in `ODD-only/en/`
> Naming: `ODD.<hex_number><category>-Name.md`

## Specification
The index MUST cover reading order and core terminology. New documents MUST update the index simultaneously.

## Mechanism
Organized below by "Getting Started / Core / Extended / Quick Start."

## Reading Order

**Getting Started**:
1. `ODD.00入门-3min-Guide.md` — Start here

**Core**:
2. `ODD.01总览-Overview.md` — Global view, five pillars, L0/L1/L1.5/L2/L3 levels
3. `ODD.02对象-Object-Model.md` — Contract, task, artifact, evidence, seal
4. `ODD.03状态-State-Machine.md` — State transitions and gate checks
5. `ODD.04证据-Evidence-Sealing.md` — Evidence, sealing, and auditing

**Extended**:
6. `ODD.07产物-Artifact-Taxonomy.md` — Artifact types and templates
7. `ODD.08管道-Pipeline-Composition.md` — Pipeline composition and dependency management
8. `ODD.0B功树-Functional-Tree.md` — Business function index and impact analysis
9. `ODD.05上下文-Context-Engineering.md` — Context injection strategies
10. `ODD.06对抗-Contract-Adversarial.md` — Clarity assessment + adversarial generation + floor/red line
11. `ODD.0C赛马-Smart-Racing.md` — Task grading, failure escalation, post-diagnosis decisions
12. `ODD.0D预警-Alert-Traffic-Light.md` — Light states, graded alerts, human decision menu
13. `ODD.0E法宝-Bug-Map-Best-Practices.md` — Three Magic Tools, bug intention map, best practices, anti-patterns, metrics
14. `ODD.09安全-Security-Performance.md` — Security and performance
15. `ODD.0F车间-Workshop-Model.md` — Role system, workshop pool scheduling, fault recovery, cross-review
16. `ODD.10验证-Native-Verification.md` — TD-AI paradigm, I/O mapping, dynamic value matching, mutation testing
17. `ODD.11版本-Version-Migration.md` — Semantic versioning, compatibility rules, migration patterns, version lifecycle
18. `ODD.12执行-Execution-Model.md` — Error model, side effects, state/concurrency, transaction boundaries and compensation

**Quick Start**:
19. `ODD.0A模板-Template-Library.md` — L1/L2/L3 + universal templates, copy and use
20. `ODD.15实战-15min-Quick-Start.md` — Hands-on: 10-min seal + 15-min team collaboration

**Reference**:
21. `ODD.14术语-Glossary-Reference.md` — 70+ terms bilingual, concept relationship diagram, academic references

**Theory & Positioning**:
22. `ODD.16LLM-Alignment-And-Training-Guide.md` — LLM alignment and training guidelines from an ODD engineering perspective
23. `ODD.17Architecture-Pure-Agent-And-Theory-Completion.md` — Theory gap analysis and pure agent design
24. `ODD.18Positioning-Why-Choose-ODD.md` — Why choose ODD: positioning against Agile, TDD, DevOps

## Role-Based Learning Paths

**Architect Path** (focus: structure and governance):
`Intro` → `01 Overview` → `02 Object Model` → `08 Pipeline` → `0B Func Tree` → `09 Security` → `11 Version` → `12 Execution`

**Developer Path** (focus: hands-on and verification):
`Intro` → `01 Overview` → `02 Object Model` → `03 State Machine` → `0A Templates` → `10 Verification` → `15 Quick Start` → `0E Bug Map`

**Assessor/Auditor Path** (focus: quality and evidence):
`Intro` → `01 Overview` → `04 Evidence` → `06 CAP` → `0F Workshop` → `0C Racing` → `0D Alert`

## Document Dependencies

The following shows prerequisite dependencies (→ means "read first"):

```
00 Intro → 01 Overview → 02 Object → 03 State Machine
                              → 04 Evidence
                              → 07 Artifact → 0B Func Tree
                                             → 0E Bug Map
                  01 Overview → 08 Pipeline
                  02 Object → 05 Context
                             → 06 CAP
                  03 State Machine → 0F Workshop → 0C Racing
                                                  → 0D Alert
                  06 CAP + 10 Verification → Can be read independently
                  09 Security, 11 Version, 12 Execution → Can be read independently (recommend 01+02 first)
                  0A Templates, 15 Quick Start → Consult anytime
                  14 Glossary → Consult anytime
```

## Core Terminology
- **Contract**: A clear agreement about work, including acceptance criteria
- **Task**: A specific work item under a contract, producing one artifact
- **Artifact**: A verifiable, concrete deliverable
- **Gate**: A checkpoint for state transitions
- **Evidence**: A verifiable record of gate checks
- **Seal**: Artifact + evidence locked and archived
- **Pipeline**: A contract-governed assembly line that promotes artifacts
- **Functional Tree**: Business function index managing the artifact network
- **Workshop**: An isolated execution environment; one contract binds to one workshop; multiple workshops run in parallel
- **Floor**: The minimum condition a contract must satisfy — missing means system unusable
- **Red Line**: A constraint that must never be violated — touching it means immediate termination
- **Racing**: Selecting executor level by task complexity; escalating after failure diagnosis
- **Traffic Light**: A graded alert system showing task health via light states
- **Three Magic Tools**: Functional Tree + Bug Intention Map + Best Practices — the core mechanism for making implicit knowledge explicit
- **Bug Intention Map**: Historical error-prone pattern library organized by artifact type
- **Best Practices**: Recommended practice library organized by artifact type
- **Anti-Pattern**: Practices to avoid, including symptoms, consequences, and solutions
- **TD-AI**: Test-Driven AI paradigm — don't trust AI's process, trust only verifiable results
- **ODD Native Verification**: Comparing AI output directly against I/O mappings in the contract, without relying on AI-generated test code
- **Mutation Testing**: Deliberately introducing bugs in code to verify test effectiveness
- **Contract Version Migration**: Version strategies, compatibility rules, and migration patterns for contract evolution
- **Unseal**: Human-authorized only; reverts a sealed artifact to rework status
- **External Display Label**: Internal states are unified; externally displayed with professional terms by artifact category
- **Execution Model**: Unified rules for error handling/side effects/state/concurrency/transactions and compensation
- **Idempotency**: Guarantee that repeated calls produce no additional side effects
- **Compensation**: Reverse undo strategy after external call failure
- **Pipeline Boundary Principle**: Decision rules for DB layer vs. application layer responsibility division
- **Intelligence Officer**: System role that assembles context before model invocation
- **17-Layer Context**: Context injection model allocated by hierarchical levels
- **Artifact Standard Library**: Standard collection providing templates/implicit requirements/common knowledge/adversarial vectors per type
- **Implicit Requirements**: Default constraints that must be injected into contracts even if not explicitly written
- **Common Knowledge**: General knowledge in the standard library that can be directly injected into context

## Document Structure Convention
Every mechanism document is organized with the following structure:
- **Intent** — Why
- **Specification** — Rules that must not be violated
- **Mechanism** — L1/L2/L3 three-level concrete implementation
- **Practice** — Selection guide and core principles

## Practice
- After adding new documents, update the index and terminology first, then publish.
- Read in order to avoid concept gaps from skipping around.

## Versioning
This document set supports versioned evolution. Any specification-level change MUST record the reason and scope of impact.
