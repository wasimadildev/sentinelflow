"""Validate critical offline invariants in GitHub workflow source files."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI = (ROOT / '.github/workflows/ci.yml').read_text()
RELEASE = (ROOT / '.github/workflows/release.yml').read_text()


class WorkflowWiringTests(unittest.TestCase):
    def test_security_ci_is_reusable_and_read_only(self):
        self.assertIn('  workflow_call:', CI)
        self.assertIn('permissions:\n  contents: read', CI)
        self.assertIn('name: REQUIRED | Security Gate', CI)

    def test_only_main_publishes(self):
        self.assertIn('branches: [main]', RELEASE)
        self.assertIn("if: github.ref == 'refs/heads/main'", RELEASE)
        self.assertNotIn('pull_request:', RELEASE)

    def test_release_depends_on_security_and_pinning(self):
        self.assertIn('needs: [security-ci]', RELEASE)
        self.assertIn('needs: [pinned-dependencies]', RELEASE)
        self.assertIn('scripts/pin_actions.py --check', RELEASE)
        self.assertIn('scripts/pin_container_images.py --check', RELEASE)

    def test_crypto_verification_is_mandatory(self):
        self.assertIn('cosign sign --yes', RELEASE)
        self.assertIn('cosign verify', RELEASE)
        self.assertIn('scripts/verify-release.sh', RELEASE)
        self.assertIn('push-to-registry: true', RELEASE)


if __name__ == '__main__':
    unittest.main()
