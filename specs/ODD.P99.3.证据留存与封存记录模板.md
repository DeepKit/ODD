---
title: "ODD.P99.3 证据留存与封存记录模板"
subtitle: "把证据对象、封存记录、解封与回滚动作压成最小模板"
version: "1.0"
author: "Yi Fu (付毅, ODDFounder, fuyi.it@live.cn)"
status: "公开征评版"
---

# ODD.P99.3 证据留存与封存记录模板

> **公开口径**：`工具层文档 / 公开征评版`

---

## 一、常见证据类型

| 证据类型 | 当前用途 | 最低字段 |
|---------|---------|---------|
| `test_report` | 证明验收条件是否通过 | `result / summary / storage_ref` |
| `coverage_report` | 证明覆盖情况 | `summary / storage_ref` |
| `mutation_report` | 证明测试是否真的在检查代码 | `mutation_score / storage_ref` |
| `review_record` | 记录人工验收或复核结论 | `reviewer / summary` |
| `override` | 记录人工覆盖门禁的理由 | `original_result / overridden_to / reason` |
| `decision_narrative` | 留下“为什么这么做”的简述 | `summary / author` |

---

## 二、最小证据模板

```yaml
evidence:
  id: ""
  evidence_type: test_report | coverage_report | mutation_report | review_record | override
  gate: quality_check | acceptance
  result: pass | fail | freeze
  summary: ""
  storage_ref: ""
  sha256: ""
  contract_id: ""
  task_id: ""
```

---

## 三、最小封存模板

```yaml
seal:
  artifact_version: ""
  artifact_ref: ""
  evidence_bundle: []
  sealed_at: ""
  sealed_by: ""
  decision_narrative: ""
```

封存最低纪律：

1. 产出物引用必须清楚
2. 证据列表必须可回查
3. 封存者必须可识别
4. 若未来需要解释“为什么这样封”，应保留 `decision_narrative`

---

## 四、最小解封模板

```yaml
unseal:
  artifact_ref: ""
  reason: ""
  by: ""
  at: ""
  follow_up: rework | rollback | hotfix
```

解封最低纪律：

1. 不允许无理由解封
2. 解封后必须进入返工、回滚或热修流程之一
3. 解封动作本身也应留痕

---

## 五、最小回滚/召回模板

```yaml
rollback:
  target_version: ""
  from_version: ""
  reason: ""
  triggered_by: ""
  impact_scope: ""

recall:
  artifact_ref: ""
  affected_consumers: []
  stop_action: pause | disable | withdraw
  compensation_path: ""
```

---

## 六、使用顺序建议

1. 用 `P99.2` 决定当前任务该过哪些门禁
2. 用本文生成证据、封存、解封与回滚记录
3. 将具体记录回链到主文、白皮书或案例索引

---

## 七、最短总句

> `ODD` 的证据与封存，不是“测过就算”，而是必须留下可回查、可解释、可回滚的记录对象。

---

**版本**：1.0
**状态**：公开征评版
