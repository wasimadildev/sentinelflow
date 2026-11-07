#!/usr/bin/env python3
"""Create and validate machine-readable metadata for one immutable image release.

Only standard library modules are used, so this works in GitHub-hosted runners.
The local metadata file is NOT a digital signature; use cosign and GitHub
attestation verification for cryptographic trust.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
IMAGE_RE = re.compile(r"^ghcr\.io/[a-z0-9_.-]+/[a-z0-9_.\-/]+$")
WORKFLOW_PATH = ".github/workflows/release.yml"
ISSUER = "https://token.actions.githubusercontent.com"


def fail(message: str) -> None:
    raise ValueError(message)


def validate_data(d: dict) -> dict:
    if not isinstance(d, dict):
        fail("release metadata must be a JSON object")
    if d.get("schema_version") != 1:
        fail("unknown release metadata schema")
    repo, image, digest, commit = [d.get(k) for k in ("repository", "image", "digest", "commit")]
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        fail("invalid GitHub owner/repository")
    if not isinstance(image, str) or not IMAGE_RE.fullmatch(image) or image != image.lower():
        fail("invalid GHCR image repository")
    if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
        fail("invalid sha256 digest")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        fail("invalid 40-character Git commit")
    expected_owner = repo.split("/", 1)[0].lower()
    if image != f"ghcr.io/{expected_owner}/sentinelflow-api":
        fail("image name does not match trusted repository owner")
    expected_ref = f"{image}@{digest}"
    expected_id = f"https://github.com/{repo}/{WORKFLOW_PATH}@refs/heads/main"
    if d.get("image_ref") != expected_ref:
        fail("image_ref does not match image and digest")
    if d.get("cosign_certificate_identity") != expected_id:
        fail("certificate identity does not match the release workflow")
    if d.get("oidc_issuer") != ISSUER:
        fail("OIDC issuer mismatch")
    if d.get("source_ref") != "refs/heads/main":
        fail("release must come from main")
    sbom = d.get("sbom")
    if not isinstance(sbom, dict) or not re.fullmatch(r"[a-f0-9]{64}", str(sbom.get("sha256", ""))):
        fail("SBOM sha256 missing or invalid")
    if sbom.get("format") != "spdx-json":
        fail("SBOM must be SPDX JSON")
    if not isinstance(d.get("created_at_utc"), str):
        fail("creation timestamp missing")
    return d


def load_metadata(path: str | Path) -> dict:
    file = Path(path)
    data = validate_data(json.loads(file.read_text(encoding="utf-8")))
    sbom_name = data["sbom"].get("path")
    if not isinstance(sbom_name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.json", sbom_name):
        fail("unsafe or missing SBOM filename")
    sbom_file = file.parent / sbom_name
    if not sbom_file.is_file():
        fail(f"SBOM file referenced in release metadata is missing: {sbom_file}")
    actual_digest = hashlib.sha256(sbom_file.read_bytes()).hexdigest()
    if actual_digest != data["sbom"]["sha256"]:
        fail("SBOM bytes do not match expected sha256 checksum")
    return data


def create(ns: argparse.Namespace) -> dict:
    sbom_path = Path(ns.sbom)
    if not sbom_path.is_file():
        fail(f"SBOM is missing: {sbom_path}")
    doc = {
        "schema_version": 1,
        "project": "SentinelFlow",
        "phase": 2,
        "repository": ns.repo,
        "commit": ns.commit,
        "source_ref": "refs/heads/main",
        "image": ns.image,
        "digest": ns.digest,
        "image_ref": f"{ns.image}@{ns.digest}",
        "cosign_certificate_identity": f"https://github.com/{ns.repo}/{WORKFLOW_PATH}@refs/heads/main",
        "oidc_issuer": ISSUER,
        "sbom": {
            "path": sbom_path.name,
            "format": "spdx-json",
            "sha256": hashlib.sha256(sbom_path.read_bytes()).hexdigest(),
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return validate_data(doc)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create", help="Create metadata after publishing and scanning")
    create_parser.add_argument("--file", required=True)
    create_parser.add_argument("--image", required=True)
    create_parser.add_argument("--digest", required=True)
    create_parser.add_argument("--repo", required=True)
    create_parser.add_argument("--commit", required=True)
    create_parser.add_argument("--sbom", required=True)
    for operation in ("verify", "get"):
        op = sub.add_parser(operation)
        op.add_argument("--file", required=True)
        if operation == "get":
            op.add_argument("--field", required=True, choices=[
                "image_ref", "image", "digest", "repository", "commit", "cosign_certificate_identity",
            ])
    return p


def main() -> int:
    ns = parser().parse_args()
    try:
        if ns.command == "create":
            data = create(ns)
            target = Path(ns.file)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"Created verified metadata: {target}")
        elif ns.command == "verify":
            load_metadata(ns.file)
            print("Metadata structure, digest format, and expected workflow identity: PASS")
        else:
            print(load_metadata(ns.file)[ns.field])
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser().exit(2, f"Release metadata validation failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
