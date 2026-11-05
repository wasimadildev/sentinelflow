# Implementation milestones and acceptance tests

## Phase 1 — Local and CI baseline (delivered files)

- [x] Node.js demo HTTP API, startup/shutdown, public metadata, health/readiness.
- [x] Automated unit tests and smoke test scripts.
- [x] Minimal nonroot container with no package installation.
- [x] GitHub Actions Gitleaks, Semgrep, selected Checkov rules, Trivy and SBOM jobs.
- [x] Aggregated security-gate job.
- [x] Kubernetes restricted base manifests (not deployed).
- [ ] Verify workflow against a new GitHub-hosted runner after pushing.
- [ ] Enable main branch ruleset to require the gate.
- [ ] Capture PR checks and artifact screenshots.

## Phase 2 — Signed, reproducible releases

- [ ] Pin every GitHub action to SHA; pin OCI images to digests; enable Dependabot updates.
- [ ] Add Docker Buildx and metadata; create deterministic commit-specific build labels.
- [ ] Publish digest to private/public sandbox registry, signed by Cosign keyless.
- [ ] Generate and verify supply-chain attestations (issuer + identity + digest).
- [ ] Require independent verification before release status passes.
- [ ] SBOM both source and image; capture license and vulnerability baselines.
- [ ] Demonstrate tampered/unsigned image fails verification.

## Phase 3 — Terraform, AWS OIDC, ECR/EKS

- [ ] Terraform plan/apply through scoped GitHub environment and IAM OIDC role.
- [ ] Security-hardened VPC, EKS, ECR, IAM policies, logging and encryption.
- [ ] Scope IAM trust to exact GitHub organization/repo/branch or environment subject.
- [ ] Terraform checks in PR and human-approved apply on protected main.
- [ ] Costs monitored with AWS budget alerts; tear-down instructions tested.

## Phase 4 — GitOps and admission security

- [ ] Repo-based QA and production overlays pinned to immutable image digests.
- [ ] Argo CD syncs QA automatically; production requires promotion approval.
- [ ] Kyverno denies unsigned images and privileged or root pods.
- [ ] Verified signed-image allowlist linked to intended build identity.
- [ ] Rollback and drift recovery tested.

## Phase 5 — Security observability and interview evidence

- [ ] Dashboards show security build stats and deployments.
- [ ] Alert on admission failures and repeated vulnerability gate failures.
- [ ] Test noncompliant IaC, leaked test-only synthetic strings, unsigned artifacts.
- [ ] Complete runbooks, threat-model reviews, architecture diagram and demo video.
- [ ] Record quantitative metrics from actual runs, not estimates.
