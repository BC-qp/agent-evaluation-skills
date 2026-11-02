#!/usr/bin/env python3
"""校验 task-distiller 产出的提纯任务包。

检查项：
- 结构：要么有 prompt.md + 四个配套文件，要么有 rejection.md；
- prompt.md 的必要章节；
- 编码（UTF-8，无乱码标记）；
- 密钥/凭据模式；
- 个人绝对路径和盘符；
- 内网链接/URL（提醒）；
- 提示词中出现模型名称或评测元信息（错误）。

只依赖 Python 标准库。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_WITH_PROMPT = [
    "prompt.md",
    "design_notes.md",
    "desensitization_log.md",
    "acceptance_checklist.md",
    "risks_and_gaps.md",
]

PROMPT_REQUIRED_HEADINGS = [
    "任务",
    "背景",
    "输入材料",
    "你的任务",
    "交付物",
    "验收标准",
    "护栏",
]

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|cookie|password|passwd|private[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+]{12,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(mysql|postgres|mongodb|redis)://[^\s'\"]+"),
]

# 命中 SECRET_PATTERNS 但包含这些占位标记时，视为已脱敏，不误报
PLACEHOLDER_MARKERS = ["<REDACTED", "REDACTED_PASSWORD", "xxxx", "CHANGEME",
                       "PLACEHOLDER", "YOUR_", "<password>", "<PASSWORD>", "示例", "占位"]

# 个人绝对路径：Windows 盘符、用户目录、UNC 路径
# 盘符前用 (?<![A-Za-z]) 避免把 "http://" 里的 "p:/" 误判为路径
ABS_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?:Users|users|Windows|Program Files|Documents and Settings)"),
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!assets|references|scripts|data|input|output)[^\s'\")，。；]+"),
    re.compile(r"/(?:home|Users|root|mnt|media)/[^\s'\")，。；]+"),
    re.compile(r"\\{2}[A-Za-z0-9_.$-]+\\[^\s'\")，。；]+"),  # UNC \\host\share
]

URL_PATTERN = re.compile(r"https?://[^\s'\")，。；]+")

MODEL_NAME_PATTERNS = [
    # 用 ASCII 字母数字做边界，避免中文相邻时 \b 失效（中文字符在 Python 里算 \w）
    re.compile(r"(?i)(?<![A-Za-z0-9])(claude code|claude|chatgpt|gpt[-\s]?[0-9](?:\.\d+)?|gemini|codex|deepseek|qwen|kimi|文心一言|通义千问)(?![A-Za-z0-9])"),
]

PROMPT_META_PATTERNS = [
    re.compile(r"这是(?:一项|一个|本次)?(?:评测|测试|对比|benchmark)", re.IGNORECASE),
    re.compile(r"(?:待测|候选)模型|所有模型|模型对比|评分(?:维度|标准|规则)"),
    re.compile(r"任务完成度|产物质量|过程效率|自主性与恢复"),
]

BAD_TEXT_MARKERS = ["?" * 4, "\ufffd", "ï»¿"]

# 常见内网/云控制台主机片段，仅作提醒
INTERNAL_HOST_HINTS = [
    "localhost", "127.0.0.1", "10.", "192.168.", "172.16.",
    ".internal", ".local", ".corp", ".lan",
    "feishu.cn", "larkoffice", "jira", "confluence", "gitlab",
    "aliyun.com", "tencent.com", "amazonaws", "console.",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def scan_secrets(text: str) -> list[str]:
    hits = []
    for pat in SECRET_PATTERNS:
        for m in pat.finditer(text):
            found = m.group(0)
            if any(mark in found for mark in PLACEHOLDER_MARKERS):
                continue
            hits.append("[已隐藏疑似凭据]")
    return hits


def scan_abs_paths(text: str) -> list[str]:
    hits = []
    for pat in ABS_PATH_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    return hits


def scan_urls(text: str) -> list[str]:
    return URL_PATTERN.findall(text)


def is_internal(url: str) -> bool:
    low = url.lower()
    return any(h in low for h in INTERNAL_HOST_HINTS)


def scan_model_names(text: str) -> list[str]:
    hits = []
    for pat in MODEL_NAME_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    return sorted(set(hits))


def validate(root: Path) -> dict[str, object]:
    result: dict[str, object] = {
        "package": str(root),
        "ok": True,
        "errors": [],
        "warnings": [],
        "mode": None,
        "files_checked": [],
    }
    errors: list[str] = result["errors"]  # type: ignore[assignment]
    warnings: list[str] = result["warnings"]  # type: ignore[assignment]

    if not root.exists() or not root.is_dir():
        errors.append("提纯产物文件夹不存在，或目标不是文件夹")
        result["ok"] = False
        return result

    has_prompt = (root / "prompt.md").exists()
    has_rejection = (root / "rejection.md").exists()

    if has_prompt and has_rejection:
        errors.append("prompt.md 与 rejection.md 同时存在：出题与拒绝只能二选一")
    if not has_prompt and not has_rejection:
        errors.append("缺少 prompt.md（也没有 rejection.md）：无法判断是出题还是拒绝")
        result["ok"] = False
        return result

    if has_rejection:
        result["mode"] = "rejection"
        files = ["rejection.md"]
    else:
        result["mode"] = "prompt"
        files = list(REQUIRED_WITH_PROMPT)
        for name in REQUIRED_WITH_PROMPT:
            if not (root / name).exists():
                errors.append(f"缺少必要文件：{name}")

    for name in files:
        p = root / name
        if not p.exists():
            continue
        result["files_checked"].append(name)  # type: ignore[union-attr]
        try:
            text = read_text(p)
        except OSError as exc:
            errors.append(f"无法读取 {name}：{exc}")
            continue

        for marker in BAD_TEXT_MARKERS:
            if marker in text:
                errors.append(f"{name} 存在乱码标记：{marker!r}")

        for hit in scan_secrets(text):
            errors.append(f"{name} 可能包含密钥/凭据：{hit}")

        for hit in scan_abs_paths(text):
            errors.append(f"{name} 包含个人绝对路径或盘符：{hit}")

        urls = scan_urls(text)
        for u in urls:
            if is_internal(u):
                errors.append(f"{name} 包含疑似内网/控制台链接：{u}")
            else:
                warnings.append(f"{name} 包含外部链接，请确认是否可外发：{u}")

    # 递归扫描包内其余文本文件（例如 inputs/ 下的输入材料），防止输入材料泄露密钥或路径
    scanned = {name for name in files}
    extra_exts = {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv",
                  ".env", ".log", ".ini", ".conf", ".toml", ".cfg", ".sql",
                  ".sh", ".tsv", ".xml", ".html"}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel in scanned:
            continue
        if p.suffix.lower() not in extra_exts:
            continue
        try:
            text = read_text(p)
        except OSError as exc:
            warnings.append(f"{rel} 无法读取，已跳过：{exc}")
            continue
        result["files_checked"].append(rel)  # type: ignore[union-attr]
        for marker in BAD_TEXT_MARKERS:
            if marker in text:
                errors.append(f"{rel} 存在乱码标记：{marker!r}")
        for hit in scan_secrets(text):
            errors.append(f"{rel} 可能包含密钥/凭据：{hit}")
        for hit in scan_abs_paths(text):
            errors.append(f"{rel} 包含个人绝对路径或盘符：{hit}")
        for u in scan_urls(text):
            if is_internal(u):
                errors.append(f"{rel} 包含疑似内网/控制台链接：{u}")
            else:
                warnings.append(f"{rel} 包含外部链接，请确认是否可外发：{u}")

    if result["mode"] == "prompt" and (root / "prompt.md").exists():
        prompt = read_text(root / "prompt.md")
        for heading in PROMPT_REQUIRED_HEADINGS:
            if heading not in prompt:
                errors.append(f"prompt.md 缺少必要章节或关键词：{heading}")
        for hit in scan_model_names(prompt):
            errors.append(f"prompt.md 出现模型名称：{hit}")
        for pattern in PROMPT_META_PATTERNS:
            match = pattern.search(prompt)
            if match:
                errors.append(f"prompt.md 出现评测或评分元信息：{match.group(0)}")

    if errors:
        result["ok"] = False
    return result


def main() -> None:
    # Windows 控制台默认可能是 GBK，统一用 UTF-8 输出，保证 --json 可被其他程序解析
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="校验 task-distiller 提纯任务包。")
    parser.add_argument("package", help="要校验的提纯产物文件夹。")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON。")
    args = parser.parse_args()

    root = Path(args.package).expanduser().resolve()
    report = validate(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"提纯产物：{report['package']}")
        print(f"模式：{report['mode']}")
        print(f"是否通过：{report['ok']}")
        print(f"检查文件：{', '.join(report['files_checked'])}")  # type: ignore[arg-type]
        for key, label in (("errors", "错误"), ("warnings", "提醒")):
            items = report[key]
            if items:
                print(f"{label}：")
                for item in items:
                    print(f"- {item}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
