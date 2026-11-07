#!/usr/bin/env python3
"""Minimal structural and size checks for a generated SPDX JSON SBOM."""
import json
import re
import sys
from pathlib import Path


def validate_file(file: Path) -> int:
    if not file.is_file() or file.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("SBOM missing or larger than 16 MiB attestation limit")
    sbom = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(sbom, dict):
        raise ValueError("SBOM must be a JSON object")
    if not re.fullmatch(r"SPDX-2\.[23]", sbom.get("spdxVersion", "")):
        raise ValueError("SBOM must be SPDX 2.2 or 2.3")
    if sbom.get("dataLicense") != "CC0-1.0":
        raise ValueError("SPDX dataLicense is not CC0-1.0")
    if not isinstance(sbom.get("packages"), list):
        raise ValueError("SBOM packages list missing")
    if not isinstance(sbom.get("creationInfo"), dict):
        raise ValueError("SPDX creationInfo missing")
    return len(sbom["packages"])


if __name__ == "__main__":
    try:
        count = validate_file(Path(sys.argv[1]))
    except (IndexError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"SPDX validation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(f"Valid SPDX JSON: {count} package entries")
