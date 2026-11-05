#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'Local security tools must be preinstalled: gitleaks, semgrep, trivy, checkov, syft.'
for tool in gitleaks semgrep trivy checkov syft; do
  command -v "$tool" >/dev/null || { echo "Missing: $tool" >&2; exit 2; }
done

mkdir -p evidence

gitleaks git . --redact --exit-code 1

semgrep scan --config p/ci --error --metrics=off apps/api/src

checkov --directory deploy/k8s/base --framework kubernetes --check CKV_K8S_8,CKV_K8S_9,CKV_K8S_20,CKV_K8S_22,CKV_K8S_23,CKV_K8S_31,CKV_K8S_37,CKV_K8S_38,CKV_K8S_40 --quiet

trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --exit-code 1 .

syft dir:. -o spdx-json=evidence/source-sbom.spdx.json

echo 'Local security scans passed; SBOM at evidence/source-sbom.spdx.json.'
