---
version: 1.0.0
status: stable
last_updated: 2026-02-11
prerequisites: []
---

# Glossary and References

## Intent
The ODD documentation uses many specialized terms and abbreviations. This document provides bilingual mapping, concept relationship diagram, and academic references for quick lookup and external communication.

## Specification
- New terms MUST be updated in this document and `ODD.00索引-Index.md`.
- Term definitions in this document are the authoritative source; index definitions are simplified.

## Mechanism

### Core Bilingual Glossary

#### Five Pillars
- Contract — 契约
- Artifact — 产出物
- Gate — 门禁
- Evidence — 证据
- Seal — 封存

#### Objects and Structures
- Task — 任务
- Pipeline — 管道
- Functional Tree — 功能树
- Dependency Graph — 依赖图
- Functional Node — 功能节点
- Artifact Type — 产出物类型
- Artifact Standard Library — 产出物标准库

#### States and Flow
- State Machine — 状态机
- Rework — 返工
- Unseal — 解封
- Sealed (state) — 封版
- Blocked — 阻塞
- Deprecated — 废弃
- External Display Label — 外部显示标签

#### Quality and Verification
- Clarity Assessment — 清晰度评估
- Adversarial Generation — 对抗生成
- Contract Adversarial Protocol (CAP) — 契约对抗协议
- Floor (minimum condition) — 地板
- Red Line (must not violate) — 红线
- Mutation Testing — 变异测试
- Mutant — 变异体
- Mutation Score — 变异分数
- ODD Native Verification — ODD 原生验证
- TD-AI — Test-Driven AI（测试驱动 AI 范式）
- Input-Output Mapping — 输入输出映射
- Dynamic Value Matching — 动态值匹配

#### Context and Knowledge
- Context Engineering — 上下文工程
- Intelligence Officer — 情报官
- 17-Layer Context Model — 17 层上下文
- Implicit Requirements — 隐式需求
- Common Knowledge Base — 常识库
- Token Budget — Token 预算
- Preset Parameter Set — 预置参数组
- Prompt Repository — 提示词存库

#### Execution and Management
- Workshop — 车间
- Workshop Pool — 车间池
- Racing (task grading/matching) — 赛马
- Traffic Light (tiered alerting) — 红绿灯
- Three Magic Tools (Functional Tree + Bug Map + Best Practices) — 三大法宝
- Bug Map (Bug Intention Map) — Bug 意向图
- Best Practices — 最佳实践
- Anti-Pattern — 反模式
- Cross-Review — 交叉审核

#### Versioning and Migration
- Contract Version Migration — 契约版本迁移
- Semantic Versioning (SemVer) — 语义化版本
- Compatibility Rules — 兼容性规则
- Version Lifecycle — 版本生命周期

#### Execution Model
- Idempotency — 幂等性
- Compensation — 补偿
- Side-Effect Declaration — 副作用声明
- Transaction Boundary — 事务边界
- Pipeline Boundary Principle — 管道边界原则

#### Roles
- Proposer — 提案者
- Challenger — 挑战者
- Attacker — 攻击者
- Arbiter — 裁决者

#### Level System
- L1 · Lightweight — L1 · 轻量
- L2 · Standard — L2 · 标准
- L3 · Strict — L3 · 严格
- L4 · Human Review (task level only) — L4 · 人工审查

#### Abbreviations
- ODD — Output-Driven Development（产出物驱动开发）
- CAP — Contract Adversarial Protocol（契约对抗协议）
- TD-AI — Test-Driven AI（测试驱动 AI）
- ES — Empirically Settled（经验可判定）
- NES — Not Empirically Settled（经验不可判定）
- DAG — Directed Acyclic Graph（有向无环图）
- SemVer — Semantic Versioning（语义化版本）

### Core Concept Relationship Diagram

```
                        ┌─────────────┐
                        │  Human Intent  │
                        └─────┬───────┘
                              ▼
                    ┌─────────────────┐
                    │     Contract     │◄── Clarity Assessment + CAP
                    └────────┬────────┘
                             │ Decompose
                    ┌────────▼────────┐
                    │       Task       │◄── Racing Grading + Workshop Assignment
                    └────────┬────────┘
                             │ Execute
                    ┌────────▼────────┐
                    │     Artifact     │◄── Three Magic Tools injection (Functional Tree + Bug Map + Best Practices)
                    └────────┬────────┘
                             │ Verify
                    ┌────────▼────────┐
                    │       Gate       │◄── ODD Native Verification + Mutation Testing
                    └────────┬────────┘
                             │ Pass
                    ┌────────▼────────┐
                    │     Evidence     │
                    └────────┬────────┘
                             │ Bind
                    ┌────────▼────────┐
                    │       Seal       │
                    └────────┬────────┘
                             │ Input
                    ┌────────▼────────┐
                    │     Pipeline     │──→ Promote to new artifact → Loop
                    └─────────────────┘

    Horizontal relations:
    Functional Tree ↔ Artifact (business location)
    Dependency Graph ↔ Artifact (technical propagation)
    Context Engineering → Intelligence Officer → 17-Layer Context → Model Call
    Artifact Standard Library → Implicit Requirements + Common Knowledge Base → Inject into Contract/Task
```

### Academic References and Theoretical Foundations

**Design by Contract**
- Bertrand Meyer, "Applying Design by Contract", IEEE Computer, 1992
- ODD extends Meyer's pre/postcondition model with adversarial generation and clarity assessment

**Mutation Testing**
- Richard Lipton, "Fault Diagnosis of Computer Programs", PhD Thesis, Carnegie Mellon, 1971
- Jia & Harman, "An Analysis and Survey of the Development of Mutation Testing", IEEE TSE, 2011
- ODD extends mutation testing from code verification to contract verification

**Property-Based Testing**
- Claessen & Hughes, "QuickCheck: A Lightweight Tool for Random Testing", ICFP, 2000
- ODD's property mappings directly inherit the idea of property-based testing

**Pipeline Architecture**
- Martin Fowler, "Pipes and Filters", Enterprise Integration Patterns
- ODD pipelines emphasize contract boundaries and seal propagation, unlike traditional dataflow pipelines

**State Machines and Formal Verification**
- David Harel, "Statecharts: A Visual Formalism for Complex Systems", Science of Computer Programming, 1987
- ODD state machines are simplified for engineering, using gates instead of full formal verification

**Semantic Versioning**
- Tom Preston-Werner, "Semantic Versioning 2.0.0", semver.org
- ODD contract version migration directly adopts SemVer

**Test Pyramid**
- Mike Cohn, "Succeeding with Agile", 2009
- ODD's 70/25/5 ratio derives from this classic model

---

## Practice
- Use Chinese terms primarily in internal communication, with English abbreviations in parentheses.
- Use English terms in external documents and API design.
- When unsure about a term, use this document as the source of truth, not the simplified index definitions.
