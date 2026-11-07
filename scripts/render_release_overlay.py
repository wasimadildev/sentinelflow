#!/usr/bin/env python3
"""Render a deployable digest-only Kustomize overlay from release metadata.

Phase 2 GENERATES the overlay; actual GitOps reconciliation belongs to Phase 4.
"""
import argparse
from pathlib import Path

from release_metadata import load_metadata

DEFAULT_BASE_IMAGE = "ghcr.io/example/sentinelflow-api"


def render(data: dict) -> str:
    # All data has been validated against strict name/digest regexes.
    return ("# Generated from a verified SentinelFlow release metadata file.\n"
            "# Do not replace immutable digests with mutable tags.\n"
            "apiVersion: kustomize.config.k8s.io/v1beta1\n"
            "kind: Kustomization\n"
            "resources:\n"
            "  - ../../base\n"
            "images:\n"
            f"  - name: {DEFAULT_BASE_IMAGE}\n"
            f"    newName: {data['image']}\n"
            f"    digest: {data['digest']}\n")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release", required=True, help="release.json")
    p.add_argument("--output", required=True, help="Write Kustomization to this path")
    ns = p.parse_args()
    data = load_metadata(ns.release)
    out = Path(ns.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print(f"Digest-only deployment overlay: {out}")


if __name__ == "__main__":
    main()
