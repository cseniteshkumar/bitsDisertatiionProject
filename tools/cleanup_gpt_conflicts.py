#!/usr/bin/env python3
"""Cleanup script to list and optionally delete .gpt_researcher conflict files.

Usage:
  python tools/cleanup_gpt_conflicts.py       # dry-run, lists files
  python tools/cleanup_gpt_conflicts.py --delete  # actually delete files

This is intentionally conservative: dry-run by default.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def find_conflicts(root: Path):
    return sorted(root.rglob('*.gpt_researcher'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--delete', action='store_true', help='Delete found files')
    args = p.parse_args()

    files = find_conflicts(ROOT / 'backend')
    if not files:
        print('No .gpt_researcher files found under backend/')
        return

    print(f'Found {len(files)} .gpt_researcher files:')
    for f in files:
        print(f)

    if args.delete:
        confirm = input('Delete these files? Type YES to confirm: ')
        if confirm.strip() == 'YES':
            for f in files:
                try:
                    f.unlink()
                except Exception as e:
                    print(f'Failed to delete {f}: {e}')
            print('Deletion complete.')
        else:
            print('Aborted. No files deleted.')
    else:
        print('\nDry run complete. To delete, re-run with `--delete`.')


if __name__ == '__main__':
    main()
