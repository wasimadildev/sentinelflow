#!/usr/bin/env bash
# Verify Cosign signer identity and GitHub SLSA provenance for a released digest.
set -euo pipefail
META="${1:-artifacts/release.json}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for binary in python3 cosign; do
  command -v "$binary" >/dev/null || { echo "Required program not found: $binary" >&2; exit 2; }
done
python3 "$SCRIPT_DIR/release_metadata.py" verify --file "$META"
field() { python3 "$SCRIPT_DIR/release_metadata.py" get --file "$META" --field "$1"; }
IMAGE_REF="$(field image_ref)"
REPOSITORY="$(field repository)"
COMMIT="$(field commit)"
IDENTITY="$(field cosign_certificate_identity)"

printf '%s\n' "Checking Cosign signature for $IMAGE_REF"
cosign verify \
  --certificate-identity "$IDENTITY" \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  "$IMAGE_REF" > /dev/null
printf '%s\n' 'PASS: signature belongs to expected workflow identity'

if [[ "${SKIP_GITHUB_ATTESTATION:-0}" == 1 ]]; then
  echo 'WARNING: GitHub build provenance verification SKIPPED by explicit configuration' >&2
  exit 0
fi
command -v gh >/dev/null || { echo 'GitHub CLI (gh) is required for attestation verification' >&2; exit 2; }
gh attestation verify "oci://$IMAGE_REF" \
  --repo "$REPOSITORY" \
  --signer-workflow "$REPOSITORY/.github/workflows/release.yml" \
  --source-ref refs/heads/main \
  --source-digest "$COMMIT" >/dev/null
printf '%s\n' 'PASS: SLSA build provenance belongs to protected main release workflow'
