#!/usr/bin/env python3
"""创建可复用的智能体评测任务包骨架。"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_template(destination: Path, overwrite: bool) -> None:
    source = skill_root() / "assets" / "templates" / "task-package"
    if not source.exists():
        raise SystemExit(f"未找到模板文件夹：{source}")
    if destination.exists():
        if not overwrite:
            raise SystemExit(f"目标文件夹已存在：{destination}")
        if destination.is_file():
            raise SystemExit(f"目标路径是文件，不是文件夹：{destination}")
    shutil.copytree(source, destination, dirs_exist_ok=overwrite)


def main() -> None:
    parser = argparse.ArgumentParser(description="创建智能体评测任务包骨架。")
    parser.add_argument("destination", help="要创建的任务包文件夹。")
    parser.add_argument("--overwrite", action="store_true", help="允许复制到已存在的文件夹。")
    args = parser.parse_args()

    dest = Path(args.destination).expanduser().resolve()
    copy_template(dest, args.overwrite)
    print(f"已创建任务包骨架：{dest}")
    print("下一步：填写《提示词.md》，把真实工具文件放入 tools/，运行任务后补充 trace_*.jsonl。")


if __name__ == "__main__":
    main()
