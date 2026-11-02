#!/usr/bin/env python3
"""校验可复用的智能体评测任务包。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|cookie)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
]

BAD_TEXT_MARKERS = ["?" * 4, "\u951f", "\ufffd"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def validate_jsonl(path: Path) -> tuple[bool, str]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError as exc:
        return False, f"无法读取：{exc}"
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return False, "jsonl 为空"
    bad = 0
    for line in nonempty:
        try:
            json.loads(line)
        except json.JSONDecodeError:
            bad += 1
    if bad:
        return False, f"全部 {len(nonempty)} 条非空记录中有 {bad} 条不是合法 JSON"
    return True, f"{len(nonempty)} 条非空 JSONL 记录"


def scan_text_files(root: Path) -> list[str]:
    issues: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name != ".env" and path.suffix.lower() not in {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv", ".env", ".ini", ".toml", ".py", ".js", ".log"}:
            continue
        try:
            text = read_text(path)
        except OSError as exc:
            issues.append(f"无法读取 {path.relative_to(root)}：{exc}")
            continue
        for marker in BAD_TEXT_MARKERS:
            if marker in text:
                issues.append(f"{path.relative_to(root)} 可能存在乱码标记：{marker!r}")
                break
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(f"{path.relative_to(root)} 可能包含密钥或敏感字段")
                break
    return issues


def validate(root: Path) -> dict[str, object]:
    result: dict[str, object] = {
        "package": str(root),
        "ok": True,
        "scope": "结构与文本检查，不验证轨迹来源真实性或任务完成质量",
        "errors": [],
        "warnings": [],
        "trace_files": [],
    }
    errors: list[str] = result["errors"]  # type: ignore[assignment]
    warnings: list[str] = result["warnings"]  # type: ignore[assignment]

    if not root.exists() or not root.is_dir():
        errors.append("任务包文件夹不存在，或目标不是文件夹")
        result["ok"] = False
        return result

    required_groups = [
        [root / "提示词.md"],
        [root / "tools"],
        [root / "tools" / "工具说明.md"],
    ]
    for group in required_groups:
        if not any(path.exists() for path in group):
            errors.append("缺少必要路径：" + " 或 ".join(str(path.relative_to(root)) for path in group))

    trace_files = sorted(root.glob("trace_*.jsonl"))
    result["trace_files"] = [p.name for p in trace_files]
    if not trace_files:
        errors.append("缺少 trace_*.jsonl")
    else:
        for trace in trace_files:
            ok, message = validate_jsonl(trace)
            if not ok:
                errors.append(f"{trace.name}: {message}")
            else:
                warnings.append(f"{trace.name}: {message}")

    setup_path = root / "环境设置.md"
    if setup_path.exists():
        setup = read_text(setup_path)
        if "API Key" in setup and "不要包含" not in setup:
            warnings.append(f"{setup_path.relative_to(root)} 提到 API Key，请检查是否已脱敏")

    errors.extend(scan_text_files(root))

    if errors:
        result["ok"] = False
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="校验智能体评测任务包。")
    parser.add_argument("package", help="要校验的任务包文件夹。")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON。")
    args = parser.parse_args()

    report = validate(Path(args.package).expanduser().resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"任务包：{report['package']}")
        print(f"是否通过：{report['ok']}")
        label = {"errors": "错误", "warnings": "提醒"}
        for key in ("errors", "warnings"):
            items = report[key]
            if items:
                print(f"{label[key]}：")
                for item in items:
                    print(f"- {item}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
