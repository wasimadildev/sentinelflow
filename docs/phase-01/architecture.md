# SentinelFlow target architecture

## Architecture diagram

![Glowing DevSecOps GitOps Pipeline Diagram](../diagrams/phase-01/Glowing%20DevSecOps%20GitOps%20Pipeline%20Diagram.png)

## Trust boundaries

1. **Developer to GitHub** — commits/PRs are untrusted. Branch rules protect trusted `main` and approvals.
2. **Repository to CI runner** — workflow files and third-party actions can execute code. Default token permissions are read-only. Never expose production secrets to PR jobs.
3. **CI to registry** — only approved `main` release job should gain OIDC-backed identity, with exact GitHub branch/environment claims. CI PR jobs do not have AWS permissions.
4. **Registry to GitOps** — only image digests with SBOM/provenance and allowed signatures can be promoted.
5. **GitOps to Kubernetes** — Argo CD service accounts may apply scoped namespaces; Kyverno validates signed images and secure pod controls. Application service accounts have no automatic API tokens.
6. **Cluster to runtime** — network isolation, pod security, encryption, audit events, least-privilege workload identity, and monitoring.

## Environment topology

- Local: MacBook, Node.js, Docker Desktop; optional kind cluster (no cloud cost).
- QA: isolated Kubernetes namespace/cluster with separate ingress and least-privilege identities.
- Production: EKS private worker nodes, managed control plane, private ECR pull path, encrypted log and image storage, scoped ingress, separate IAM roles.
- GitOps: dedicated repo (recommended) with `environments/qa` and `environments/prod`; Argo CD pulls this repository. Promotion updates digest through a reviewed PR, not a mutable tag.

## Planned IaC modules

- `network`: subnet layout, VPC endpoints, NAT tradeoffs, network controls.
- `eks`: managed nodes, audit logs, managed add-ons, KMS encryption where applicable.
- `ecr`: repositories, scan policy, immutable tags, lifecycle policy.
- `github-oidc`: narrowly scoped IAM role trusted only for approved repo/branch/environment.
- `observability`: centralized logs, metrics, alerts and retention.

## Deployment flow (target phases 2–4)

1. PR opens → tests, secrets, SAST, IaC, image CVE gates; no AWS access.
2. Required PR ruleset passes and reviewer approves → merge to protected main.
3. Release workflow rebuilds from trusted commit, produces SBOM and provenance, signs image, pushes by digest to ECR using OIDC. Do not reuse an untrusted PR artifact.
4. Promotion PR changes only the immutable digest in GitOps configuration.
5. Reviewer approves QA or production promotion; Argo CD reconciles.
6. Kyverno validates signer identity, immutable digest, and workload restrictions; policy failure blocks admission.
7. Monitoring checks readiness, latency, runtime alerts; rollback changes GitOps commit to prior approved digest.

## Security failure modes & mitigations

- PR manipulates workflow: protected paths, PR review, read-only token, OIDC restricted to main/environment.
- Leaked GitHub token: minimal permissions, short lifecycle, no cloud role for PR.
- Poisoned build image/action: immutable digest pinning, Dependabot review, provenance and signature checks.
- Registry tag replacement: immutable digest and signature verification.
- Compromised Kubernetes workload: nonroot, read-only root filesystem, no service account token, NetworkPolicy, dedicated namespace.
- Insufficient scanner coverage: multiple scanning layers, dependency updates, policy tests, vulnerability exception review.
- Broken release: GitOps rollback, health probes, audit log retention.

## Phase-1 boundary

Only the left-hand checks and sample application are implemented. Cloud identity, ECR, signing, GitOps, Kyverno, and production-grade observability are designed but not installed or claimed to be working.
