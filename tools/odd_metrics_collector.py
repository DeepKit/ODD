#!/usr/bin/env python3
"""
ODD 实证数据采集工具
从 Progee 项目的 git 历史、契约文件、测试文件中采集 ODD 相关指标。

采集指标：
1. 返工率：git 历史中 fix/rework 提交占总提交的比例
2. 契约质量：契约文件的验收条件数量、覆盖度
3. Bug 拦截模式：bug 修复的分布和模式
4. 测试覆盖：测试文件数量和测试密度
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict


# ─── 配置 ───────────────────────────────────────────────

PROGEE_SRV = Path("D:/_Progs/srv/progee")
PROGEE_CONTRACTS = PROGEE_SRV / ".progee" / "contracts"
ODD_DEMO = Path("D:/_Progs/02Business/odd-demo")
OUTPUT_DIR = Path("D:/_Progs/01Center/ODD/ODD-main/tools/metrics_output")


# ─── Git 分析 ───────────────────────────────────────────

def get_git_log(repo_path, max_count=500):
    """获取 git 提交历史"""
    cmd = [
        "git", "-C", str(repo_path), "log",
        f"--max-count={max_count}",
        "--format=%H|%ai|%s",
        "--no-merges"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "message": parts[2]
            })
    return commits


def classify_commit(message):
    """分类提交类型"""
    msg = message.lower()
    if re.match(r'^fix[\(:]', msg) or 'bug' in msg or 'bugfix' in msg:
        return "fix"
    elif re.match(r'^feat[\(:]', msg) or msg.startswith("feat"):
        return "feature"
    elif re.match(r'^refactor[\(:]', msg) or msg.startswith("refactor"):
        return "refactor"
    elif re.match(r'^docs[\(:]', msg) or msg.startswith("docs"):
        return "docs"
    elif re.match(r'^test[\(:]', msg) or msg.startswith("test"):
        return "test"
    elif re.match(r'^chore[\(:]', msg) or msg.startswith("chore"):
        return "chore"
    elif '修复' in message or 'fix' in msg:
        return "fix"
    elif '添加' in message or '实现' in message or 'add' in msg:
        return "feature"
    elif '重构' in message or '迁移' in message:
        return "refactor"
    elif '文档' in message or '更新' in message and 'doc' in msg:
        return "docs"
    else:
        return "other"


def analyze_rework_rate(commits):
    """分析返工率"""
    total = len(commits)
    if total == 0:
        return {}

    classified = Counter(classify_commit(c["message"]) for c in commits)

    fix_count = classified.get("fix", 0)
    feature_count = classified.get("feature", 0)
    refactor_count = classified.get("refactor", 0)

    # 返工率 = fix 提交 / (feature + fix) 提交
    productive = feature_count + fix_count
    rework_rate = fix_count / productive if productive > 0 else 0

    # Bug 密度 = fix 提交 / 总提交
    bug_density = fix_count / total if total > 0 else 0

    return {
        "total_commits": total,
        "commit_types": dict(classified),
        "rework_rate": round(rework_rate * 100, 1),
        "bug_density": round(bug_density * 100, 1),
        "fix_count": fix_count,
        "feature_count": feature_count,
        "refactor_count": refactor_count
    }


def analyze_bug_patterns(commits):
    """分析 Bug 模式"""
    bug_commits = [c for c in commits if classify_commit(c["message"]) == "fix"]
    patterns = defaultdict(int)

    for c in bug_commits:
        msg = c["message"]
        # 提取 BUG-XXX 编号
        bug_ids = re.findall(r'BUG-(\d+)', msg)
        if bug_ids:
            for bid in bug_ids:
                patterns[f"BUG-{bid}"] = 1

        # 分类 bug 类型
        if '测试' in msg or 'test' in msg.lower():
            patterns["test_related"] += 1
        if '字段' in msg or 'field' in msg.lower() or '列' in msg:
            patterns["schema_mismatch"] += 1
        if 'API' in msg or 'api' in msg or '接口' in msg:
            patterns["api_issue"] += 1
        if '验证' in msg or 'valid' in msg.lower():
            patterns["validation_issue"] += 1
        if '软删除' in msg or 'soft.?delete' in msg.lower():
            patterns["soft_delete_issue"] += 1

    return {
        "total_bugs": len(bug_commits),
        "unique_bug_ids": len([k for k in patterns if k.startswith("BUG-")]),
        "bug_categories": {k: v for k, v in patterns.items() if not k.startswith("BUG-")},
        "sample_bug_messages": [c["message"][:80] for c in bug_commits[:10]]
    }


# ─── 契约分析 ────────────────────────────────────────────

def analyze_contracts(contracts_dir):
    """分析契约文件质量"""
    if not contracts_dir.exists():
        return {"error": f"Directory not found: {contracts_dir}"}

    contracts = []
    for f in sorted(contracts_dir.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            contracts.append({
                "file": f.name,
                "id": data.get("id", "unknown"),
                "name": data.get("name", "unknown"),
                "status": data.get("status", "unknown"),
                "acceptance_criteria_count": len(data.get("acceptance_criteria", [])),
                "requirements_count": len(data.get("requirements", [])),
                "has_test_plan": "test_plan" in data,
                "has_response_schema": "response_schema" in data,
                "has_example_response": "example_response" in data,
                "has_implementation_notes": "implementation_notes" in data,
                "has_definition_of_done": "definition_of_done" in data,
            })
        except (json.JSONDecodeError, KeyError) as e:
            contracts.append({"file": f.name, "error": str(e)})

    valid = [c for c in contracts if "error" not in c]

    if not valid:
        return {"total_contracts": 0, "contracts": contracts}

    ac_counts = [c["acceptance_criteria_count"] for c in valid]
    req_counts = [c["requirements_count"] for c in valid]

    return {
        "total_contracts": len(contracts),
        "valid_contracts": len(valid),
        "acceptance_criteria": {
            "total": sum(ac_counts),
            "avg_per_contract": round(sum(ac_counts) / len(valid), 1),
            "min": min(ac_counts),
            "max": max(ac_counts),
        },
        "requirements": {
            "total": sum(req_counts),
            "avg_per_contract": round(sum(req_counts) / len(valid), 1),
        },
        "completeness": {
            "with_test_plan": sum(1 for c in valid if c["has_test_plan"]),
            "with_response_schema": sum(1 for c in valid if c["has_response_schema"]),
            "with_example_response": sum(1 for c in valid if c["has_example_response"]),
            "with_implementation_notes": sum(1 for c in valid if c["has_implementation_notes"]),
            "with_definition_of_done": sum(1 for c in valid if c["has_definition_of_done"]),
        },
        "contracts": valid
    }


# ─── 测试分析 ────────────────────────────────────────────

def analyze_tests(repo_path):
    """分析测试文件"""
    test_files = list(repo_path.rglob("test_*.py")) + list(repo_path.rglob("*_test.py"))
    # 排除 .git 和 __pycache__
    test_files = [f for f in test_files if ".git" not in str(f) and "__pycache__" not in str(f)]

    total_test_functions = 0
    total_lines = 0
    files_info = []

    for tf in test_files:
        try:
            content = tf.read_text(encoding="utf-8")
            lines = len(content.split("\n"))
            test_funcs = len(re.findall(r'def test_', content))
            total_test_functions += test_funcs
            total_lines += lines
            files_info.append({
                "file": str(tf.relative_to(repo_path)),
                "test_functions": test_funcs,
                "lines": lines
            })
        except Exception:
            pass

    # 统计源码文件
    py_files = list(repo_path.rglob("*.py"))
    py_files = [f for f in py_files if ".git" not in str(f) and "__pycache__" not in str(f)
                and "test_" not in f.name and "_test.py" not in f.name]

    return {
        "test_files": len(test_files),
        "source_files": len(py_files),
        "test_to_source_ratio": round(len(test_files) / len(py_files), 2) if py_files else 0,
        "total_test_functions": total_test_functions,
        "total_test_lines": total_lines,
        "avg_tests_per_file": round(total_test_functions / len(test_files), 1) if test_files else 0,
    }


# ─── 封存记录分析 ─────────────────────────────────────────

def analyze_seal_records(demo_path):
    """分析封存记录"""
    seal_files = list(demo_path.rglob("seal_*.json"))
    seals = []

    for sf in seal_files:
        try:
            with open(sf, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            verification = data.get("artifacts", {}).get("verification", {})
            checks = verification.get("checks", [])
            passed_checks = sum(1 for c in checks if c.get("passed"))
            failed_checks = sum(1 for c in checks if not c.get("passed"))
            critical_checks = [c for c in checks if c.get("severity") == "critical"]
            critical_passed = sum(1 for c in critical_checks if c.get("passed"))

            seals.append({
                "seal_id": data.get("seal_id", "unknown"),
                "timestamp": data.get("timestamp", "unknown"),
                "overall_passed": verification.get("passed", False),
                "critical_failed": verification.get("critical_failed", False),
                "total_checks": len(checks),
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "critical_total": len(critical_checks),
                "critical_passed": critical_passed,
                "check_details": [
                    {"rule": c.get("rule"), "severity": c.get("severity"), "passed": c.get("passed")}
                    for c in checks
                ]
            })
        except Exception as e:
            seals.append({"file": str(sf), "error": str(e)})

    return {
        "total_seals": len(seals),
        "passed": sum(1 for s in seals if s.get("overall_passed")),
        "failed": sum(1 for s in seals if not s.get("overall_passed") and "error" not in s),
        "seals": seals
    }


# ─── 主程序 ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ODD 实证数据采集工具 v1.0")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"generated_at": datetime.now().isoformat(), "data_sources": []}

    # 1. Git 历史分析
    print("\n[1/4] 分析 Progee 项目 Git 历史...")
    if PROGEE_SRV.exists():
        commits = get_git_log(PROGEE_SRV)
        rework = analyze_rework_rate(commits)
        bugs = analyze_bug_patterns(commits)
        report["git_analysis"] = {
            "repo": str(PROGEE_SRV),
            "rework_metrics": rework,
            "bug_patterns": bugs
        }
        report["data_sources"].append(str(PROGEE_SRV))
        print(f"  总提交数: {rework.get('total_commits', 0)}")
        print(f"  返工率: {rework.get('rework_rate', 'N/A')}%")
        print(f"  Bug 密度: {rework.get('bug_density', 'N/A')}%")
        print(f"  Bug 数量: {bugs.get('total_bugs', 0)}")
    else:
        print(f"  跳过: {PROGEE_SRV} 不存在")

    # 2. 契约分析
    print("\n[2/4] 分析契约文件...")
    if PROGEE_CONTRACTS.exists():
        contracts = analyze_contracts(PROGEE_CONTRACTS)
        report["contract_analysis"] = contracts
        report["data_sources"].append(str(PROGEE_CONTRACTS))
        print(f"  契约总数: {contracts.get('total_contracts', 0)}")
        print(f"  验收条件总数: {contracts.get('acceptance_criteria', {}).get('total', 0)}")
        print(f"  平均验收条件/契约: {contracts.get('acceptance_criteria', {}).get('avg_per_contract', 'N/A')}")
    else:
        print(f"  跳过: {PROGEE_CONTRACTS} 不存在")

    # 3. 测试分析
    print("\n[3/4] 分析测试文件...")
    if PROGEE_SRV.exists():
        tests = analyze_tests(PROGEE_SRV)
        report["test_analysis"] = tests
        print(f"  测试文件数: {tests['test_files']}")
        print(f"  源码文件数: {tests['source_files']}")
        print(f"  测试/源码比: {tests['test_to_source_ratio']}")
        print(f"  测试函数总数: {tests['total_test_functions']}")
    else:
        print(f"  跳过: {PROGEE_SRV} 不存在")

    # 4. 封存记录分析
    print("\n[4/4] 分析封存记录...")
    if ODD_DEMO.exists():
        seals = analyze_seal_records(ODD_DEMO)
        report["seal_analysis"] = seals
        report["data_sources"].append(str(ODD_DEMO))
        print(f"  封存记录数: {seals['total_seals']}")
        print(f"  通过: {seals['passed']}")
        print(f"  失败: {seals['failed']}")
    else:
        print(f"  跳过: {ODD_DEMO} 不存在")

    # 输出报告
    output_file = OUTPUT_DIR / f"odd_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"报告已保存: {output_file}")

    # 生成摘要表格
    print(f"\n{'=' * 60}")
    print("ODD 实证数据摘要")
    print(f"{'=' * 60}")

    if "git_analysis" in report:
        r = report["git_analysis"]["rework_metrics"]
        b = report["git_analysis"]["bug_patterns"]
        print(f"\n{'─' * 40}")
        print(f"{'指标':<25} {'值':>12}")
        print(f"{'─' * 40}")
        print(f"{'总提交数':<25} {r.get('total_commits', 'N/A'):>12}")
        print(f"{'Feature 提交':<25} {r.get('feature_count', 'N/A'):>12}")
        print(f"{'Fix 提交':<25} {r.get('fix_count', 'N/A'):>12}")
        print(f"{'Refactor 提交':<25} {r.get('refactor_count', 'N/A'):>12}")
        print(f"{'返工率':<25} {str(r.get('rework_rate', 'N/A')) + '%':>12}")
        print(f"{'Bug 密度':<25} {str(r.get('bug_density', 'N/A')) + '%':>12}")
        print(f"{'已知 Bug 编号数':<25} {b.get('unique_bug_ids', 'N/A'):>12}")

    if "contract_analysis" in report:
        c = report["contract_analysis"]
        ac = c.get("acceptance_criteria", {})
        print(f"\n{'─' * 40}")
        print(f"{'契约总数':<25} {c.get('total_contracts', 'N/A'):>12}")
        print(f"{'验收条件总数':<25} {ac.get('total', 'N/A'):>12}")
        print(f"{'平均验收条件/契约':<25} {ac.get('avg_per_contract', 'N/A'):>12}")
        print(f"{'最少验收条件':<25} {ac.get('min', 'N/A'):>12}")
        print(f"{'最多验收条件':<25} {ac.get('max', 'N/A'):>12}")

    if "test_analysis" in report:
        t = report["test_analysis"]
        print(f"\n{'─' * 40}")
        print(f"{'测试文件数':<25} {t['test_files']:>12}")
        print(f"{'源码文件数':<25} {t['source_files']:>12}")
        print(f"{'测试/源码比':<25} {t['test_to_source_ratio']:>12}")
        print(f"{'测试函数总数':<25} {t['total_test_functions']:>12}")

    if "seal_analysis" in report:
        s = report["seal_analysis"]
        print(f"\n{'─' * 40}")
        print(f"{'封存记录数':<25} {s['total_seals']:>12}")
        print(f"{'验证通过':<25} {s['passed']:>12}")
        print(f"{'验证失败（被拦截）':<25} {s['failed']:>12}")

    print(f"{'─' * 40}")
    print(f"\n数据采集完成。")
    return report


if __name__ == "__main__":
    main()
