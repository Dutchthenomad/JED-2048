#!/usr/bin/env python3
"""
Generate a machine-readable project index (JSON).

Usage:
  python scripts/generate_index.py [--out docs/PROJECT_INDEX.json] [--exclude DIR ...]

Defaults:
  - Excludes: venv, __pycache__
  - Output: docs/PROJECT_INDEX.json
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


@dataclass
class FileEntry:
    path: str
    ext: str
    size_bytes: int


def collect_files(root: Path, excludes: List[str]) -> List[Path]:
    ex_dirs = {e.rstrip("/") for e in excludes}
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in ex_dirs]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            files.append(Path(dirpath) / name)
    return files


def build_index(root: Path, files: List[Path]) -> Dict:
    entries: List[FileEntry] = []
    counts: Dict[str, int] = {}
    for f in sorted(files):
        rel = f.relative_to(root).as_posix()
        ext = f.suffix.lstrip(".").lower()
        size = f.stat().st_size if f.exists() else 0
        entries.append(FileEntry(path=rel, ext=ext, size_bytes=size))
        counts[ext] = counts.get(ext, 0) + 1

    index = {
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(entries),
        "counts_by_ext": dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "files": [asdict(e) for e in entries],
    }
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="docs/PROJECT_INDEX.json",
        help="Output JSON path (relative to project root)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["venv", "__pycache__", "validation_data"],
        help="Directory names to exclude at any depth",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    files = collect_files(project_root, excludes=args.exclude)
    index = build_index(project_root, files)

    out_path = project_root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Wrote index to: {out_path}")


if __name__ == "__main__":
    main()

