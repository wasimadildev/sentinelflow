#!/usr/bin/env python3
"""Resolve GitHub Actions refs to immutable commit SHAs via git ls-remote.

Usage:
    python3 scripts/pin_actions.py --apply   # Requires network + git
    python3 scripts/pin_actions.py --check   # Offline fail-closed inspection

This script does not claim to audit the behavior of third-party actions. Review
release tags and their source before pinning. Dependabot can update pinned SHAs.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / '.github/workflows/ci.yml', ROOT / '.github/workflows/release.yml']
USES = re.compile(r'^(\s*(?:- )?uses:\s+)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([\w.-]+)(\s*(?:#.*)?)$', re.MULTILINE)
SHA = re.compile(r'^[0-9a-f]{40}$')


def resolve(action: str, tag: str) -> str:
    url = f'https://github.com/{action}.git'
    ref = f'refs/tags/{tag}'
    result = subprocess.run(['git', 'ls-remote', '--tags', url, ref, ref + '^{}'],
                            text=True, capture_output=True, timeout=35, check=True)
    matches = {}
    for line in result.stdout.splitlines():
        value, _, name = line.partition('\t')
        if SHA.fullmatch(value):
            matches[name] = value
    commit = matches.get(ref + '^{}', matches.get(ref))
    if not commit:
        raise RuntimeError(f'Cannot resolve action {action}@{tag}: git ref not found')
    return commit


def check() -> int:
    failed = False
    for path in FILES:
        text = path.read_text()
        for match in USES.finditer(text):
            action, version = match.group(2), match.group(3)
            if not SHA.fullmatch(version):
                print(f'NOT PINNED: {path.relative_to(ROOT)}: {action}@{version}')
                failed = True
    if failed:
        print('Action pinning incomplete. Run: python3 scripts/pin_actions.py --apply')
        return 2
    print('PASS: every third-party GitHub Action ref is pinned to a 40-character commit')
    return 0


def apply() -> int:
    cache = {}
    planned = {}
    for path in FILES:
        old = path.read_text()

        def replace(match):
            pre, action, version, post = match.groups()
            if SHA.fullmatch(version):
                return match.group(0)
            key = (action, version)
            if key not in cache:
                cache[key] = resolve(action, version)
                print(f'Resolved {action}@{version} -> {cache[key]}')
            return f'{pre}{action}@{cache[key]}{post} # {version}'

        planned[path] = USES.sub(replace, old)
    # Avoid partial changes if any external tag fails to resolve.
    for path, new in planned.items():
        path.write_text(new)
        print(f'Pinned {path.relative_to(ROOT)}')
    return check()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--apply', action='store_true')
    args = p.parse_args()
    try:
        return check() if args.check else apply()
    except (OSError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        p.exit(2, f'Cannot safely pin GitHub Actions: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
