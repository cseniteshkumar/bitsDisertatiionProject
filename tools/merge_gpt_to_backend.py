#!/usr/bin/env python3
"""Merge `gpt_researcher/` into `backend/` and update imports.

Usage:
  python3 tools/merge_gpt_to_backend.py [--delete-original]

What it does (safe defaults):
 - Creates `archive/backend.<timestamp>/` containing the original
   `gpt_researcher/` tree for rollback.
 - Copies files from `gpt_researcher/` into `backend/` recursively.
   - If a target file already exists in `backend/`, the original is kept and
     the incoming file is saved as `<name>.gpt_researcher` to avoid data loss.
 - Replaces usages of `gpt_researcher` with `backend` across the repository
   (skips `.venv`, `archive`, and `backend` directories when searching).
 - Optionally deletes the original `gpt_researcher/` after successful merge
   when `--delete-original` is provided.

This script must be run from the repository root.
"""
import argparse
import os
import shutil
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
G_SRC = ROOT / "gpt_researcher"
BACKEND = ROOT / "backend"
ARCHIVE = ROOT / "archive"


def copy_tree_safe(src: Path, dst: Path):
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            sfile = Path(root) / f
            tfile = target_dir / f
            if tfile.exists():
                # avoid overwrite: write incoming file alongside with suffix
                alt = target_dir / (f + ".gpt_researcher")
                shutil.copy2(sfile, alt)
                print(f"Conflict: kept existing {tfile}; copied incoming to {alt}")
            else:
                shutil.copy2(sfile, tfile)


def replace_imports(root: Path):
    skip_dirs = {".venv", "archive", "backend"}
    for path in root.rglob("*.py"):
        if any(part in skip_dirs for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        new = text.replace("from backend", "from backend").replace(
            "import backend", "import backend"
        ).replace("backend.", "backend.")
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"Patched imports in {path}")


def ensure_archive():
    ARCHIVE.mkdir(exist_ok=True)


def run(delete_original: bool):
    if not G_SRC.exists():
        print("gpt_researcher/ not found — nothing to do.")
        return 1

    ensure_archive()
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = ARCHIVE / f"backend.{ts}"
    print(f"Archiving {G_SRC} → {backup}")
    shutil.copytree(G_SRC, backup)

    print(f"Copying {G_SRC} → {BACKEND}")
    BACKEND.mkdir(parents=True, exist_ok=True)
    copy_tree_safe(G_SRC, BACKEND)

    print("Updating imports across repository (skipping .venv, archive, backend)")
    replace_imports(ROOT)

    if delete_original:
        trash = ARCHIVE / f"backend.DELETED.{ts}"
        print(f"Deleting original gpt_researcher/ and moving to {trash}")
        shutil.move(str(G_SRC), str(trash))
    else:
        print("Original gpt_researcher/ retained in place (archive copy created).")

    print("Done. Please run: python3 tools/smoke_test.py and review results.")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--delete-original", action="store_true", help="Remove original gpt_researcher after merge")
    args = p.parse_args()
    sys.exit(run(args.delete_original))
