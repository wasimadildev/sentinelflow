#!/usr/bin/env python3
"""Offline Phase 2 tests (no GitHub token, Docker daemon or network needed)."""
import argparse
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

BASE = Path(__file__).resolve().parents[1]


def getmodule(name):
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


metadata = getmodule("release_metadata")
sbom = getmodule("validate_sbom")
import sys
sys.path.insert(0, str(BASE))
from render_release_overlay import render


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tempdir = Path(self.temp.name)
        self.sbom = self.tempdir / "sample.spdx.json"
        self.sbom.write_text(json.dumps({
            "spdxVersion": "SPDX-2.3", "dataLicense": "CC0-1.0",
            "packages": [{"name": "fixture"}], "creationInfo": {"creators": ["Tool: fixture"]},
        }))
        self.args = SimpleNamespace(
            image="ghcr.io/example/sentinelflow-api",
            digest="sha256:" + "a" * 64,
            repo="example/sentinelflow-zero-trust-devsecops",
            commit="b" * 40,
            sbom=str(self.sbom),
        )

    def test_spdx_structure(self):
        self.assertEqual(sbom.validate_file(self.sbom), 1)

    def test_create_metadata(self):
        data = metadata.create(self.args)
        self.assertEqual(data["image_ref"], f"{self.args.image}@{self.args.digest}")
        self.assertTrue(data["cosign_certificate_identity"].endswith("@refs/heads/main"))
        self.assertRegex(data["sbom"]["sha256"], r"^[a-f0-9]{64}$")

    def test_digest_validation_rejects_short_digest(self):
        self.args.digest = "sha256:abc"
        with self.assertRaises(ValueError):
            metadata.create(self.args)

    def test_ref_tampering_fails(self):
        data = metadata.create(self.args)
        data["image_ref"] = "ghcr.io/example/other@" + self.args.digest
        with self.assertRaises(ValueError):
            metadata.validate_data(data)

    def test_untrusted_workflow_identity_fails(self):
        data = metadata.create(self.args)
        data["cosign_certificate_identity"] = "https://github.com/attacker/repo"
        with self.assertRaises(ValueError):
            metadata.validate_data(data)

    def test_bad_repo_fails(self):
        self.args.repo = "../../bad"
        with self.assertRaises(ValueError):
            metadata.create(self.args)

    def test_overlay_is_digest_only(self):
        overlay = render(metadata.create(self.args))
        self.assertIn("digest: sha256:" + "a" * 64, overlay)
        self.assertIn("newName: ghcr.io/example/sentinelflow-api", overlay)
        self.assertIn("resources:\n  - ../../base", overlay)
        self.assertNotIn("newTag:", overlay)

    def test_json_roundtrip(self):
        data = metadata.create(self.args)
        path = self.tempdir / "release.json"
        path.write_text(json.dumps(data))
        self.assertEqual(metadata.load_metadata(path), data)

    def test_sbom_tamper_is_detected(self):
        data = metadata.create(self.args)
        path = self.tempdir / "release.json"
        path.write_text(json.dumps(data))
        self.sbom.write_text(self.sbom.read_text() + " ")
        with self.assertRaises(ValueError):
            metadata.load_metadata(path)

    def test_wrong_ghcr_owner_is_rejected(self):
        self.args.image = "ghcr.io/attacker/sentinelflow-api"
        with self.assertRaises(ValueError):
            metadata.create(self.args)

    def test_sbom_missing_packages_rejected(self):
        self.sbom.write_text('{"spdxVersion":"SPDX-2.3", "dataLicense":"CC0-1.0", "creationInfo":{}}')
        with self.assertRaises(ValueError):
            sbom.validate_file(self.sbom)


if __name__ == "__main__":
    unittest.main()
