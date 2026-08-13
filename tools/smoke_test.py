#!/usr/bin/env python3
"""Smoke-test: compile .py files and attempt safe imports.

Run from the repo root: `python tools/smoke_test.py`
This checks syntax via `py_compile` and tries to import key packages without calling network.
"""
import os
import sys
from pathlib import Path
import py_compile
import importlib


ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".venv", "venv", "__pycache__", "node_modules", "benchmark_results"}

# Ensure repo root is on sys.path so imports like `import backend` work
sys.path.insert(0, str(ROOT))


def find_py_files(root: Path):
    for p in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        yield p


def compile_files(files):
    ok = []
    errs = []
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True)
            ok.append(f)
        except Exception as e:
            errs.append((f, e))
    return ok, errs


def try_imports(modules):
    ok = []
    errs = []
    for m in modules:
        try:
            importlib.import_module(m)
            ok.append(m)
        except Exception as e:
            errs.append((m, e))
    return ok, errs


def main():
    print(f"Repo root: {ROOT}")

    files = list(find_py_files(ROOT))
    print(f"Found {len(files)} Python files (excluding common virtualenv dirs)")

    print("Compiling files (syntax check)...")
    ok, errs = compile_files(files)
    print(f"  Compiled OK: {len(ok)}; Errors: {len(errs)}")
    for f, e in errs[:20]:
        print(f"  ERROR {f}: {e}")

    # Try safe imports of key packages / modules used as entrypoints
    modules = [
        "gpt_researcher",
        "backend.server.app",
        "backend.run_server",
        # archived: "multi_agents.main",
        "cli",
        "main",
    ]

    print("\nAttempting safe imports of common entry modules (may fail if deps missing)...")
    okm, errm = try_imports(modules)
    print(f"  Imported OK: {len(okm)}; Failed: {len(errm)}")
    for m, e in errm:
        print(f"  IMPORT ERROR {m}: {type(e).__name__}: {e}")

    if errs or errm:
        print("\nSMOKE TEST: ISSUES FOUND")
        sys.exit(2)
    else:
        print("\nSMOKE TEST: ALL GOOD (syntax + imports) -- note: some runtime behavior still requires env keys/deps")
        sys.exit(0)


if __name__ == "__main__":
    main()
