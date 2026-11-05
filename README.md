# SentinelFlow — Enterprise Zero-Trust DevSecOps Platform

**Phase 1: Secure application + CI security gates.** This is a standalone demonstration project, not a production deployment. No AWS credentials or AWS resources are required in Phase 1.

## What runs today

- Minimal, dependency-free Node.js HTTP API, secure headers, health/readiness routes.
- Native automated tests, coverage, local smoke tests.
- Docker runtime using Google's distroless Node.js 22 nonroot image.
- Restricted Kubernetes baseline: nonroot, capabilities dropped, seccomp, probes, bounded resources, restricted namespace, minimal service account, network policy.
- GitHub Actions checks: Gitleaks, Semgrep, Checkov selected secure-pod-policy gate, Trivy image vulnerability gate, Syft SPDX SBOM.
- Required *Security Gate* aggregate job. The gate is effective as a merge control only when explicitly required by your branch protection or ruleset.

## Requirements

- Node.js 22 and npm for local application tests.
- Docker Desktop for local container builds/runs (optional for API tests).
- A GitHub repository in your **personal account** for the Gitleaks Action without an organization license. For organization-owned repos, configure `GITLEAKS_LICENSE` following Gitleaks' documentation.
- GitHub-hosted Ubuntu 24.04 runners for CI. If self-hosting, keep runner version compatible with the Node 24-based actions.

## Run in 5 commands

```bash
cd sentinelflow-phase1
cd apps/api && npm ci --ignore-scripts --no-audit && npm test && cd ../..
make smoke
make docker-build
make docker-run
# Open a separate terminal:
curl -i http://localhost:8080/healthz
```

A successful health response is `{"status":"ok"}` with `HTTP/1.1 200 OK`.

## API paths

| Verb | Path | Result |
|---|---|---|
| GET | /healthz | `{ "status": "ok" }` |
| GET | /readyz | `{ "ready": true }` |
| GET | /api/v1/info | Minimal public service metadata |
| Other | Any | 404 or 405 |

## GitHub setup

1. Create a new empty repository named `sentinelflow-zero-trust-devsecops` on your GitHub personal account.
2. Copy the repository files from this project folder into that repository and push to `main`.
3. Open **Actions**, select **SentinelFlow | Phase 1 Security CI**, and verify its checks.
4. In GitHub repository **Settings → Rules → Rulesets** (or branch protection), require **REQUIRED | Security Gate** on `main`. Require a pull request and one approval. Note that some enforcement capabilities depend on plan and public/private repository settings.
5. Use a feature branch and open a PR against main. The required check must be green before merging.

**Important:** A workflow failing on a known vulnerability or Kubernetes policy is functioning as intended. Investigate and remediate it rather than disabling the gate. Gitleaks scans full Git history, including prior secrets; rotate any exposed credential, even if removed in a later commit.

## Local checks

```bash
make test
make coverage
make smoke
make docker-build
make docker-run
```

If Gitleaks, Semgrep, Trivy, Checkov, and Syft are installed locally, `make local-security` runs all five checks. GitHub Actions can run them without local installation.

## K8s manifest validation (no deploy required)

```bash
kubectl kustomize deploy/k8s/base
kubectl apply --dry-run=client -k deploy/k8s/base
```

The image in `deploy/k8s/base/deployment.yaml` is intentionally a placeholder: **do not deploy it unchanged**. Replace it with an image you publish, preferably by immutable digest. The initial deny-by-default NetworkPolicy permits only peer application pods to call the API; add a narrowly scoped ingress-controller allowance in the GitOps phase. Not every Kubernetes CNI enforces network policies—validate enforcement in your cluster.

## Architecture and plans

- [System architecture](docs/architecture.md)
- [Phase milestones and acceptance criteria](docs/roadmap.md)
- [Threat model](docs/threat-model.md)
- [Incident/runbook notes](docs/operations.md)
- [Observed validation results and limitations](docs/validation.md)
- [Future cloud modules](infra/terraform/README.md)
- [Future GitOps modules](gitops/argocd/README.md)

## Safety, cost, and engineering notes

- Phase 1 uses no AWS resources, so there is no EKS bill.
- Checkov is a **blocking selected-check baseline** (probes, nonroot, privilege escalation, capabilities, seccomp, service-account tokens, and read-only filesystem), not every Checkov control. Require digest checks and expand all-policy compliance after publishing an image in Phase 2.
- CI uses third-party action version tags and two unpinned image references for ease of initial setup; **Phase 2 must pin all referenced actions/images to reviewed immutable digests** and configure update automation. This is deliberately not yet complete zero-trust security.
- `ignore-unfixed: true` means the image gate ignores vulnerabilities without a fix. Record this exception and decide the production policy during Phase 2.
- The Node demo has no third-party runtime packages, so a dependency scanner has limited findings. Add a realistic service in later phases.
- The project's CI prevents merges only if GitHub branch protection is configured. It does not automatically create AWS environments.

## Contributing and security policies

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the pull-request template. Dependabot updates are configured for GitHub Actions, npm, and the runtime Dockerfile.

## Portfolio proof

Save redacted screenshots of: passing unit tests, failed security scan with a deliberately unsafe *lab fixture*, subsequent fixed PR, aggregated gate, SBOM artifact, Docker nonroot identity, and K8s policy results. Do not commit live credentials or sensitive logs.

### References

- https://docs.github.com/en/actions/how-tos/secure-your-work
- https://github.com/gitleaks/gitleaks-action
- https://github.com/aquasecurity/trivy-action
- https://github.com/anchore/sbom-action
- https://github.com/bridgecrewio/checkov-action
- https://semgrep.dev/docs/
- https://kyverno.io/docs/policy-types/cluster-policy/verify-images/overview/
- https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/
