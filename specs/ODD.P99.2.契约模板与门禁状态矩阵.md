---
title: "ODD.P99.2 契约模板与门禁状态矩阵"
subtitle: "把契约成熟度、任务等级、门禁结果与状态迁移压成同一张表"
version: "1.0"
author: "Yi Fu (付毅, ODDFounder, fuyi.it@live.cn)"
status: "公开征评版"
---

# ODD.P99.2 契约模板与门禁状态矩阵

> **公开口径**：`工具层文档 / 公开征评版`

---

## 一、契约成熟度矩阵

| 成熟度 | 当前含义 | 最低要求 | 能否进入自动门禁 |
|--------|---------|---------|----------------|
| `draft` | 草案，允许自然语言与问题澄清 | 有标题、有基本范围 | 否 |
| `agreed` | 团队已确认大致理解一致 | 有范围、关键边界、主要验收点 | 只允许局部人工门禁 |
| `formal` | 可进入标准执行流的正式契约 | 验收条件、边界条件、错误条件、必要字段齐全 | 是 |

最短判断：

- `draft` 负责发现问题
- `agreed` 负责形成共识
- `formal` 才负责进入门禁

---

## 二、任务等级与默认门禁

| 等级 | 典型场景 | 默认门禁 | 封存强度 |
|------|---------|---------|---------|
| `L0` | 已有项目兼容接入 | 现有测试/CI + 人工确认 | Git commit/tag 级 |
| `L1` | 个人小任务 | `quality_check` | 轻封存 |
| `L1.5` | 个人 + AI | `quality_check` + 最小证据留存 | 轻封存 + 本地哈希 |
| `L2` | 小团队协作 | `quality_check` + `acceptance` | 标准封存 |
| `L3` | 高风险或关键系统 | `quality_check` + `acceptance` + 高强度审计/对抗/复核 | 强封存 |

---

## 三、门禁结果矩阵

| 结果 | 当前含义 | 默认去向 |
|------|---------|---------|
| `PASS` | 当前门禁通过 | 进入下一状态 |
| `FAIL` | 当前门禁明确不通过 | 回到 `rework / in_progress` |
| `FREEZE` | 当前门禁不应继续自动推进 | 进入 `freeze`，等待人工裁决 |
| `CONFLICT` | 契约本身出现冲突或互斥条件 | 返回契约层修订 |

---

## 四、任务状态矩阵

| 状态 | 含义 | 允许进入条件 | 典型出口 |
|------|------|-------------|---------|
| `blocked` | 被依赖或外部条件阻塞 | 依赖未满足 | `pending` |
| `pending` | 已建任务，尚未执行 | 契约已至少达到 `agreed` | `in_progress` |
| `in_progress` | 正在执行 | 已有人或系统接手 | `quality_check` |
| `quality_check` | 自动检查阶段 | 最低执行产物已提交 | `acceptance / rework / freeze` |
| `acceptance` | 人工或更高位验收阶段 | 自动门禁通过 | `done / sealed / rework / freeze` |
| `done` | 一般完成态 | 非强封存场景 | `sealed` 或归档 |
| `sealed` | 已封存正式版本 | 证据齐全且允许锁定 | `unseal` |
| `rework` | 被打回返工 | 门禁失败或需求修订 | `in_progress` |
| `freeze` | 暂停自动推进 | 高冲突、高风险或信息不足 | `acceptance / rework / pending` |

---

## 五、最小模板

### 5.1 L1 契约模板

```yaml
contract:
  id: ""
  title: ""
  maturity: formal
  acceptance_criteria:
    - criterion: ""
  boundary_cases:
    - ""
```

### 5.2 L2 任务模板

```yaml
task:
  id: ""
  title: ""
  contract_id: ""
  state: pending
  task_level: L2
  artifact_ref: ""
  acceptance_criteria:
    - ""
```

### 5.3 门禁记录模板

```yaml
gate_result:
  gate: quality_check | acceptance
  result: PASS | FAIL | FREEZE | CONFLICT
  evidence_refs: []
  summary: ""
  next_state: ""
```

---

## 六、使用顺序建议

1. 先用 `P99.1` 确认对象和术语没有漂移
2. 再用本文确认契约成熟度、任务等级与门禁状态
3. 需要证据与封存格式时，再回引 `P99.3`

---

## 七、最短总句

> `ODD` 的门禁不是“过没过”两个字，而是一套把契约成熟度、任务等级、状态迁移和封存强度绑在一起的矩阵。

---

**版本**：1.0
**状态**：公开征评版
