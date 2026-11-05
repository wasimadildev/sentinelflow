# Security policy

This repository is a learning and portfolio project. Please do not open public issues containing real tokens, passwords, infrastructure identifiers, or exploit data. For suspected security flaws, use GitHub private vulnerability reporting if enabled, or contact the repository maintainer privately. Rotate credentials independently of whether a report or pull request has been opened.

## Reporting guidelines

Provide a minimal sanitized reproduction, affected versions/commit, expected versus actual behavior, and potential impact. Avoid testing against systems you do not own or administer.

## Security baselines

Phase 1 has read-only CI permissions, test-only application, nonroot container, selected Checkov Kubernetes checks, Gitleaks, Semgrep, and Trivy. Signing, enforced admission policy, and AWS identity protections are scheduled for later phases. Do not treat the Phase-1 demo as production approved.
