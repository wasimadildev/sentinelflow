#!/usr/bin/env python3
"""Pin distroless base and Semgrep scanner images to registry manifest digests.

Use Docker Desktop + internet for --apply; --check is offline.
"""
from __future__ import annotations
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / 'apps/api/Dockerfile'
CI = ROOT / '.github/workflows/ci.yml'
BASE_TAG = 'gcr.io/distroless/nodejs22-debian12:nonroot'
SCAN_TAG = 'semgrep/semgrep:latest'
DIGEST = re.compile(r'^sha256:[0-9a-f]{64}$')


def get_digest(tag: str) -> str:
    proc = subprocess.run(
        ['docker', 'buildx', 'imagetools', 'inspect', '--format', '{{.Manifest.Digest}}', tag],
        check=True, capture_output=True, text=True, timeout=70)
    digest = proc.stdout.strip()
    if not DIGEST.fullmatch(digest):
        raise RuntimeError(f'Invalid image manifest digest from registry for {tag}: {digest!r}')
    return digest


def check() -> int:
    dockerfile, ci = DOCKERFILE.read_text(), CI.read_text()
    ok_base = bool(re.search(r'^FROM gcr\.io/distroless/nodejs22-debian12@sha256:[a-f0-9]{64}', dockerfile, re.M))
    ok_scan = bool(re.search(r'semgrep/semgrep@sha256:[a-f0-9]{64}', ci))
    print(f'Distroless base pinned: {ok_base}; Semgrep scanner pinned: {ok_scan}')
    return 0 if ok_base and ok_scan else 2


def apply() -> int:
    base_digest = get_digest(BASE_TAG)
    scan_digest = get_digest(SCAN_TAG)
    dockerfile = DOCKERFILE.read_text()
    ci = CI.read_text()
    base_pattern = r'gcr\.io/distroless/nodejs22-debian12(?:\:nonroot|@sha256:[0-9a-f]{64})'
    scan_pattern = r'semgrep/semgrep(?:\:latest|@sha256:[0-9a-f]{64})'
    dockerfile, n1 = re.subn(base_pattern, f'gcr.io/distroless/nodejs22-debian12@{base_digest}', dockerfile)
    ci, n2 = re.subn(scan_pattern, f'semgrep/semgrep@{scan_digest}', ci)
    if n1 != 1 or n2 != 1:
        raise RuntimeError('Expected exactly one base and one Semgrep reference; no files changed')
    DOCKERFILE.write_text(dockerfile)
    CI.write_text(ci)
    print(f'Pinned distroless base to {base_digest}')
    print(f'Pinned Semgrep scanner to {scan_digest}')
    return check()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    args = p.parse_args()
    try:
        raise SystemExit(check() if args.check else apply())
    except (RuntimeError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        p.exit(2, f'Unable to pin container images: {e}\n')
