#!/usr/bin/env python3
"""
ODD 实证数据综合采集工具 v2.0
从 Progee 项目采集可复现的实证数据，供 Paper-E1 使用。

输出 8 个 JSON 数据集 + 1 个汇总报告。
仅使用 Python 标准库，无外部依赖。
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
SCRIPT_DIR = Path(__file__).resolve().parent


def env_path(name):
    raw = os.environ.get(name, "").strip()
    return Path(raw).expanduser() if raw else None


PROGEE_SRV = env_path("ODD_PROGEE_REPO")
PROGEE_CONTRACTS = PROGEE_SRV / ".progee" / "contracts" if PROGEE_SRV else None
ODD_DEMO = env_path("ODD_DEMO_REPO")
OUTPUT_DIR = env_path("ODD_METRICS_OUTPUT") or (SCRIPT_DIR / "metrics_output")


def run_git(repo, *args):
    cmd = ["git", "-C", str(repo)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()


def classify_commit(msg):
    """分类提交类型，支持中英文关键词"""
    m = msg.lower()
    if re.match(r'^fix[\(:]', m) or 'bugfix' in m:
        return "fix"
    if re.match(r'^feat[\(:]', m) or m.startswith("feat"):
        return "feature"
    if re.match(r'^refactor[\(:]', m) or m.startswith("refactor"):
        return "refactor"
    if re.match(r'^docs[\(:]', m) or m.startswith("docs"):
        return "docs"
    if re.match(r'^test[\(:]', m) or m.startswith("test"):
        return "test"
    if re.match(r'^chore[\(:]', m) or m.startswith("chore"):
        return "chore"
    # Chinese keywords
    if '修复' in msg or 'fix' in m:
        return "fix"
    if '添加' in msg or '实现' in msg:
        return "feature"
    if '重构' in msg or '迁移' in msg:
        return "refactor"
    if '文档' in msg or '记录' in msg:
        return "docs"
    if '测试' in msg:
        return "test"
    return "other"


# ═══════════════════════════════════════════════════════════
# 1. COMMIT TIMELINE
# ═══════════════════════════════════════════════════════════
def collect_commit_timeline():
    """每个提交的完整信息：hash, date, author, message, type, 文件变更统计"""
    print("  [1/8] commit_timeline...")
    raw = run_git(PROGEE_SRV, "log", "--no-merges", "--format=COMMIT_SEP%n%H%n%aI%n%an%n%s", "--numstat")
    commits = []
    blocks = raw.split("COMMIT_SEP\n")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if len(lines) < 4:
            continue
        h, date, author, message = lines[0], lines[1], lines[2], lines[3]
        added, deleted, files_changed = 0, 0, 0
        for fl in lines[4:]:
            fl = fl.strip()
            if not fl:
                continue
            parts = fl.split("\t")
            if len(parts) >= 2:
                a = int(parts[0]) if parts[0] != '-' else 0
                d = int(parts[1]) if parts[1] != '-' else 0
                added += a
                deleted += d
                files_changed += 1
        commits.append({
            "hash": h, "date": date, "author": author, "message": message,
            "type": classify_commit(message),
            "files_changed": files_changed, "lines_added": added, "lines_deleted": deleted
        })
    print(f"    {len(commits)} commits collected")
    return commits


# ═══════════════════════════════════════════════════════════
# 2. BUG LIFECYCLE
# ═══════════════════════════════════════════════════════════
def collect_bug_lifecycle(commits):
    """每个 BUG-XXX 的生命周期：首次提及、修复时间、影响文件、根因分类"""
    print("  [2/8] bug_lifecycle...")
    bugs = defaultdict(lambda: {"mentions": [], "fix_date": None, "files": set(), "category": "other"})

    for c in commits:
        ids = re.findall(r'BUG-(\d+)', c["message"])
        for bid in ids:
            key = f"BUG-{bid}"
            bugs[key]["mentions"].append(c["date"])
            if c["type"] == "fix":
                bugs[key]["fix_date"] = c["date"]
            # categorize
            msg = c["message"]
            if '字段' in msg or 'field' in msg.lower() or 'schema' in msg.lower() or '列' in msg:
                bugs[key]["category"] = "schema_mismatch"
            elif '测试' in msg or 'test' in msg.lower():
                bugs[key]["category"] = "test_related"
            elif 'API' in msg or 'api' in msg or '接口' in msg:
                bugs[key]["category"] = "api_issue"
            elif '验证' in msg or 'valid' in msg.lower():
                bugs[key]["category"] = "validation_issue"
            elif '软删除' in msg or 'soft' in msg.lower() and 'delete' in msg.lower():
                bugs[key]["category"] = "soft_delete_issue"

    result = []
    for bug_id, info in sorted(bugs.items()):
        mentions = sorted(info["mentions"])
        first = mentions[0] if mentions else None
        fix = info["fix_date"]
        ttf = None
        if first and fix:
            try:
                t1 = datetime.fromisoformat(first)
                t2 = datetime.fromisoformat(fix)
                ttf = round((t2 - t1).total_seconds() / 3600, 1)
            except Exception:
                pass
        result.append({
            "bug_id": bug_id,
            "first_mention": first,
            "fix_date": fix,
            "time_to_fix_hours": ttf,
            "mention_count": len(mentions),
            "category": info["category"]
        })
    print(f"    {len(result)} bugs tracked")
    return result


# ═══════════════════════════════════════════════════════════
# 3. CONTRACT QUALITY
# ═══════════════════════════════════════════════════════════
def collect_contract_quality():
    """每个契约文件的质量指标和完整度评分"""
    print("  [3/8] contract_quality...")
    contracts = []
    if not PROGEE_CONTRACTS or not PROGEE_CONTRACTS.exists():
        print("    contract directory not found; skipping")
        return contracts
    for f in sorted(PROGEE_CONTRACTS.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            optional_fields = [
                "test_plan", "response_schema", "example_response",
                "implementation_notes", "definition_of_done"
            ]
            present = sum(1 for field in optional_fields if field in data and data[field])
            completeness = round(present / len(optional_fields) * 100)

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
                "file_size_bytes": f.stat().st_size,
                "completeness_score": completeness
            })
        except Exception as e:
            contracts.append({"file": f.name, "error": str(e)})
    print(f"    {len(contracts)} contracts analyzed")
    return contracts


# ═══════════════════════════════════════════════════════════
# 4. TEST DENSITY
# ═══════════════════════════════════════════════════════════
def collect_test_density():
    """每个测试文件的测试函数数、行数、断言数（支持 Python 和 Delphi）"""
    print("  [4/8] test_density...")
    test_files = []
    total_funcs, total_asserts, total_lines = 0, 0, 0

    # Python 测试文件
    for tf in sorted(PROGEE_SRV.rglob("test_*.py")):
        if ".git" in str(tf) or "__pycache__" in str(tf):
            continue
        try:
            content = tf.read_text(encoding="utf-8")
            lines = len(content.split("\n"))
            funcs = len(re.findall(r'def test_', content))
            asserts = len(re.findall(r'\bassert\b', content))
            total_funcs += funcs
            total_asserts += asserts
            total_lines += lines
            test_files.append({
                "path": str(tf.relative_to(PROGEE_SRV)),
                "test_functions": funcs,
                "lines": lines,
                "assertions": asserts,
                "language": "Python"
            })
        except Exception:
            pass

    # Delphi 测试文件 (DUnitX) - 支持 Test*.pas 和 *_Test.pas
    for tf in sorted(PROGEE_SRV.rglob("Test*.pas")):
        if ".git" in str(tf) or "__pycache__" in str(tf) or "bin" in str(tf):
            continue
        try:
            content = tf.read_text(encoding="utf-8", errors="replace")
            lines = len(content.split("\n"))
            # DUnitX 测试方法: [Test] 或 procedure TestXXX
            funcs = len(re.findall(r'\[Test\]|\bprocedure\s+Test', content, re.IGNORECASE))
            # DUnitX 断言: Assert.AreEqual, Assert.IsTrue, etc.
            asserts = len(re.findall(r'\bAssert\.', content, re.IGNORECASE))
            total_funcs += funcs
            total_asserts += asserts
            total_lines += lines
            test_files.append({
                "path": str(tf.relative_to(PROGEE_SRV)),
                "test_functions": funcs,
                "lines": lines,
                "assertions": asserts,
                "language": "Delphi"
            })
        except Exception:
            pass

    # 也检查 tests/ 目录下的所有 .pas 文件
    tests_dir = PROGEE_SRV / "tests"
    if tests_dir.exists():
        for tf in sorted(tests_dir.rglob("*.pas")):
            if tf.name.startswith("Test"):
                continue  # 已经在上面处理过
            if ".git" in str(tf) or "__pycache__" in str(tf) or "bin" in str(tf):
                continue
            try:
                content = tf.read_text(encoding="utf-8", errors="replace")
                lines = len(content.split("\n"))
                funcs = len(re.findall(r'\[Test\]|\bprocedure\s+Test', content, re.IGNORECASE))
                asserts = len(re.findall(r'\bAssert\.', content, re.IGNORECASE))
                if funcs > 0:  # 只统计包含测试的文件
                    total_funcs += funcs
                    total_asserts += asserts
                    total_lines += lines
                    test_files.append({
                        "path": str(tf.relative_to(PROGEE_SRV)),
                        "test_functions": funcs,
                        "lines": lines,
                        "assertions": asserts,
                        "language": "Delphi"
                    })
            except Exception:
                pass

    # source files (Python + Delphi)
    src_files = [f for f in PROGEE_SRV.rglob("*.py")
                 if ".git" not in str(f) and "__pycache__" not in str(f)
                 and "test_" not in f.name and "_test" not in f.name]
    # Delphi 源文件
    src_files += [f for f in PROGEE_SRV.rglob("*.pas")
                  if ".git" not in str(f) and "__pycache__" not in str(f)
                  and "bin" not in str(f)
                  and not f.name.startswith("Test")]
    src_lines = 0
    for sf in src_files:
        try:
            src_lines += len(sf.read_text(encoding="utf-8", errors="replace").split("\n"))
        except Exception:
            pass

    print(f"    {len(test_files)} test files, {total_funcs} functions, {total_asserts} assertions")
    return {
        "test_files": test_files,
        "aggregate": {
            "test_file_count": len(test_files),
            "source_file_count": len(src_files),
            "test_to_source_ratio": round(len(test_files) / max(len(src_files), 1), 3),
            "total_test_functions": total_funcs,
            "total_assertions": total_asserts,
            "total_test_lines": total_lines,
            "total_source_lines": src_lines,
            "test_lines_to_source_lines_ratio": round(total_lines / max(src_lines, 1), 3),
            "avg_assertions_per_test": round(total_asserts / max(total_funcs, 1), 1)
        }
    }


# ═══════════════════════════════════════════════════════════
# 5. CODE CHURN
# ═══════════════════════════════════════════════════════════
def collect_code_churn(commits):
    """每个源文件的变更频率和代码搅动率"""
    print("  [5/8] code_churn...")
    raw = run_git(PROGEE_SRV, "log", "--no-merges", "--format=COMMIT_SEP %H %aI", "--numstat")
    file_stats = defaultdict(lambda: {
        "commits": 0, "added": 0, "deleted": 0, "dates": []
    })

    current_hash, current_date = None, None
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("COMMIT_SEP"):
            parts = line.split()
            current_hash = parts[1] if len(parts) > 1 else None
            current_date = parts[2] if len(parts) > 2 else None
        elif line and current_hash:
            parts = line.split("\t")
            if len(parts) >= 3:
                a = int(parts[0]) if parts[0] != '-' else 0
                d = int(parts[1]) if parts[1] != '-' else 0
                path = parts[2]
                file_stats[path]["commits"] += 1
                file_stats[path]["added"] += a
                file_stats[path]["deleted"] += d
                if current_date:
                    file_stats[path]["dates"].append(current_date)

    result = []
    for path, stats in sorted(file_stats.items()):
        dates = sorted(stats["dates"])
        result.append({
            "path": path,
            "total_commits": stats["commits"],
            "lines_added": stats["added"],
            "lines_deleted": stats["deleted"],
            "churn_rate": stats["added"] + stats["deleted"],
            "is_test_file": "test_" in path.lower() or "_test." in path.lower(),
            "first_commit": dates[0] if dates else None,
            "last_commit": dates[-1] if dates else None
        })
    result.sort(key=lambda x: x["churn_rate"], reverse=True)
    print(f"    {len(result)} files tracked")
    return result


# ═══════════════════════════════════════════════════════════
# 6. REWORK ANALYSIS
# ═══════════════════════════════════════════════════════════
def collect_rework_analysis(commits, code_churn):
    """深度返工分析：fix-after-feature、测试通过率时间线、bug 热点文件"""
    print("  [6/8] rework_analysis...")

    # fix-after-feature within 48h
    fix_after_feature = 0
    for i, c in enumerate(commits):
        if c["type"] == "fix" and i + 1 < len(commits):
            prev = commits[i + 1]  # git log is reverse chronological
            if prev["type"] == "feature":
                try:
                    t1 = datetime.fromisoformat(prev["date"])
                    t2 = datetime.fromisoformat(c["date"])
                    if (t2 - t1).total_seconds() < 48 * 3600:
                        fix_after_feature += 1
                except Exception:
                    pass

    # test pass rate timeline from commit messages
    pass_rate_timeline = []
    for c in commits:
        matches = re.findall(r'(\d+)%\s*[→\->]+\s*(\d+)%', c["message"])
        for before, after in matches:
            pass_rate_timeline.append({
                "date": c["date"],
                "message": c["message"][:80],
                "before_pct": int(before),
                "after_pct": int(after),
                "improvement": int(after) - int(before)
            })

    # commit type distribution
    types = Counter(c["type"] for c in commits)
    total = len(commits)

    # bug hotspot files (top 20 most-fixed files)
    fix_commits_raw = run_git(PROGEE_SRV, "log", "--no-merges", "--grep=fix", "-i",
                              "--format=COMMIT_SEP", "--numstat")
    fix_file_counts = Counter()
    for line in fix_commits_raw.split("\n"):
        line = line.strip()
        if line and not line.startswith("COMMIT_SEP"):
            parts = line.split("\t")
            if len(parts) >= 3:
                fix_file_counts[parts[2]] += 1
    bug_hotspots = [{"file": f, "fix_count": c} for f, c in fix_file_counts.most_common(20)]

    # weekly commit distribution
    weekly = defaultdict(lambda: {"feature": 0, "fix": 0, "refactor": 0, "other": 0})
    for c in commits:
        try:
            dt = datetime.fromisoformat(c["date"])
            week = dt.strftime("%Y-W%W")
            t = c["type"]
            if t in ("feature",):
                weekly[week]["feature"] += 1
            elif t == "fix":
                weekly[week]["fix"] += 1
            elif t == "refactor":
                weekly[week]["refactor"] += 1
            else:
                weekly[week]["other"] += 1
        except Exception:
            pass

    print(f"    fix-after-feature: {fix_after_feature}, pass rate entries: {len(pass_rate_timeline)}")
    return {
        "fix_after_feature_48h": fix_after_feature,
        "test_pass_rate_timeline": pass_rate_timeline,
        "commit_type_distribution": dict(types),
        "commit_type_percentages": {k: round(v / total * 100, 1) for k, v in types.items()},
        "refactor_ratio": round(types.get("refactor", 0) / total * 100, 1),
        "bug_hotspot_files": bug_hotspots,
        "weekly_commit_distribution": dict(sorted(weekly.items()))
    }


# ═══════════════════════════════════════════════════════════
# 7. SEAL VERIFICATION
# ═══════════════════════════════════════════════════════════
def collect_seal_verification():
    """封存验证记录的详细分析"""
    print("  [7/8] seal_verification...")
    seals = []
    if not ODD_DEMO or not ODD_DEMO.exists():
        print("    seal directory not found; skipping")
        return seals
    for sf in sorted(ODD_DEMO.rglob("seal_*.json")):
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            v = data.get("artifacts", {}).get("verification", {})
            checks = v.get("checks", [])
            by_severity = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
            for ch in checks:
                sev = ch.get("severity", "unknown")
                by_severity[sev]["total"] += 1
                if ch.get("passed"):
                    by_severity[sev]["passed"] += 1
                else:
                    by_severity[sev]["failed"] += 1

            contract = data.get("artifacts", {}).get("contract", {})
            contract_info = contract.get("contract", {})
            implicit_reqs = contract_info.get("implicit_requirements", [])

            seals.append({
                "seal_id": data.get("seal_id"),
                "timestamp": data.get("timestamp"),
                "overall_passed": v.get("passed", False),
                "critical_failed": v.get("critical_failed", False),
                "total_checks": len(checks),
                "checks_by_severity": dict(by_severity),
                "failed_rules": [
                    {"rule": ch["rule"], "severity": ch["severity"], "found": ch.get("found")}
                    for ch in checks if not ch.get("passed")
                ],
                "passed_rules": [
                    {"rule": ch["rule"], "severity": ch["severity"]}
                    for ch in checks if ch.get("passed")
                ],
                "implicit_requirements_count": len(implicit_reqs),
                "implicit_requirements": [
                    {"id": r["id"], "name": r["name"], "severity": r["severity"]}
                    for r in implicit_reqs
                ],
                "artifact_type": contract.get("artifact_type"),
                "artifact_name": contract.get("artifact_name")
            })
        except Exception as e:
            seals.append({"file": str(sf), "error": str(e)})
    print(f"    {len(seals)} seal records analyzed")
    return seals


# ═══════════════════════════════════════════════════════════
# 8. SUMMARY REPORT
# ═══════════════════════════════════════════════════════════
def build_summary(commits, bugs, contracts, tests, churn, rework, seals):
    """汇总报告，适合直接引用到论文中"""
    print("  [8/8] summary_report...")

    valid_contracts = [c for c in contracts if "error" not in c]
    ac_counts = [c["acceptance_criteria_count"] for c in valid_contracts]
    completeness_scores = [c["completeness_score"] for c in valid_contracts]

    dates = []
    for c in commits:
        try:
            dates.append(datetime.fromisoformat(c["date"]))
        except Exception:
            pass
    date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}" if dates else "N/A"

    types = Counter(c["type"] for c in commits)
    fix_count = types.get("fix", 0)
    feat_count = types.get("feature", 0)
    productive = fix_count + feat_count

    seal_passed = sum(1 for s in seals if isinstance(s, dict) and s.get("overall_passed"))
    seal_failed = sum(1 for s in seals if isinstance(s, dict) and not s.get("overall_passed") and "error" not in s)

    return {
        "project_stats": {
            "total_commits": len(commits),
            "date_range": date_range,
            "total_source_files": tests["aggregate"]["source_file_count"],
            "total_source_lines": tests["aggregate"]["total_source_lines"],
            "total_test_files": tests["aggregate"]["test_file_count"],
            "total_test_lines": tests["aggregate"]["total_test_lines"],
            "primary_language": "Delphi (Object Pascal)",
            "framework": "FireMonkey + PostgreSQL"
        },
        "quality_metrics": {
            "rework_rate_pct": round(fix_count / max(productive, 1) * 100, 1),
            "bug_density_pct": round(fix_count / max(len(commits), 1) * 100, 1),
            "test_to_source_ratio": tests["aggregate"]["test_to_source_ratio"],
            "test_lines_to_source_ratio": tests["aggregate"]["test_lines_to_source_lines_ratio"],
            "total_test_functions": tests["aggregate"]["total_test_functions"],
            "total_assertions": tests["aggregate"]["total_assertions"],
            "avg_assertions_per_test": tests["aggregate"]["avg_assertions_per_test"]
        },
        "contract_metrics": {
            "total_contracts": len(valid_contracts),
            "avg_acceptance_criteria": round(sum(ac_counts) / max(len(ac_counts), 1), 1),
            "min_acceptance_criteria": min(ac_counts) if ac_counts else 0,
            "max_acceptance_criteria": max(ac_counts) if ac_counts else 0,
            "avg_completeness_score": round(sum(completeness_scores) / max(len(completeness_scores), 1), 1),
            "contracts_with_test_plan": sum(1 for c in valid_contracts if c["has_test_plan"]),
            "contracts_with_response_schema": sum(1 for c in valid_contracts if c["has_response_schema"]),
        },
        "bug_metrics": {
            "total_tracked_bugs": len(bugs),
            "bugs_with_fix": sum(1 for b in bugs if b["fix_date"]),
            "avg_time_to_fix_hours": round(
                sum(b["time_to_fix_hours"] for b in bugs if b["time_to_fix_hours"] is not None) /
                max(sum(1 for b in bugs if b["time_to_fix_hours"] is not None), 1), 1
            ),
            "bug_categories": dict(Counter(b["category"] for b in bugs))
        },
        "verification_metrics": {
            "total_seal_attempts": len(seals),
            "seal_passed": seal_passed,
            "seal_rejected": seal_failed,
            "rejection_rate_pct": round(seal_failed / max(len(seals), 1) * 100, 1),
            "critical_defects_caught": sum(
                len(s.get("failed_rules", [])) for s in seals
                if isinstance(s, dict) and "error" not in s
            )
        },
        "commit_distribution": {
            "by_type": dict(types),
            "by_type_pct": {k: round(v / max(len(commits), 1) * 100, 1) for k, v in types.items()},
            "refactor_ratio_pct": rework["refactor_ratio"],
            "fix_after_feature_48h": rework["fix_after_feature_48h"]
        },
        "code_churn_top10": [
            {"file": c["path"], "churn": c["churn_rate"], "commits": c["total_commits"]}
            for c in churn[:10]
        ]
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def save_json(data, filename):
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"    -> {path}")


def main():
    print("=" * 60)
    print("ODD Empirical Data Collector v2.0")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    if not PROGEE_SRV or not PROGEE_SRV.exists():
        raise SystemExit(
            "Missing source repository. Set environment variable ODD_PROGEE_REPO to the local reference repo path."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all datasets
    print("\nCollecting datasets...")
    commits = collect_commit_timeline()
    bugs = collect_bug_lifecycle(commits)
    contracts = collect_contract_quality()
    tests = collect_test_density()
    churn = collect_code_churn(commits)
    rework = collect_rework_analysis(commits, churn)
    seals = collect_seal_verification()
    summary = build_summary(commits, bugs, contracts, tests, churn, rework, seals)

    # Save all datasets
    print("\nSaving datasets...")
    save_json(commits, "1_commit_timeline.json")
    save_json(bugs, "2_bug_lifecycle.json")
    save_json(contracts, "3_contract_quality.json")
    save_json(tests, "4_test_density.json")
    save_json(churn, "5_code_churn.json")
    save_json(rework, "6_rework_analysis.json")
    save_json(seals, "7_seal_verification.json")
    save_json(summary, "8_summary_report.json")

    # Print summary table
    s = summary
    print(f"\n{'=' * 60}")
    print("SUMMARY FOR PAPER")
    print(f"{'=' * 60}")
    print(f"\nProject: Progee ({s['project_stats']['framework']})")
    print(f"Period: {s['project_stats']['date_range']}")
    print(f"Commits: {s['project_stats']['total_commits']}")
    print(f"Source: {s['project_stats']['total_source_files']} files, {s['project_stats']['total_source_lines']} LOC")
    print(f"Tests: {s['project_stats']['total_test_files']} files, {s['quality_metrics']['total_test_functions']} functions, {s['quality_metrics']['total_assertions']} assertions")
    print(f"\n--- Quality ---")
    print(f"Rework rate: {s['quality_metrics']['rework_rate_pct']}%")
    print(f"Bug density: {s['quality_metrics']['bug_density_pct']}%")
    print(f"Test/source ratio: {s['quality_metrics']['test_to_source_ratio']}")
    print(f"Avg assertions/test: {s['quality_metrics']['avg_assertions_per_test']}")
    print(f"\n--- Contracts ---")
    print(f"Total: {s['contract_metrics']['total_contracts']}")
    print(f"Avg acceptance criteria: {s['contract_metrics']['avg_acceptance_criteria']}")
    print(f"Avg completeness: {s['contract_metrics']['avg_completeness_score']}%")
    print(f"\n--- Bugs ---")
    print(f"Tracked: {s['bug_metrics']['total_tracked_bugs']}")
    print(f"Avg time to fix: {s['bug_metrics']['avg_time_to_fix_hours']}h")
    print(f"Categories: {s['bug_metrics']['bug_categories']}")
    print(f"\n--- Verification ---")
    print(f"Seal attempts: {s['verification_metrics']['total_seal_attempts']}")
    print(f"Rejected: {s['verification_metrics']['seal_rejected']}")
    print(f"Critical defects caught: {s['verification_metrics']['critical_defects_caught']}")
    print(f"\n{'=' * 60}")
    print("All datasets saved. Data is reproducible.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
