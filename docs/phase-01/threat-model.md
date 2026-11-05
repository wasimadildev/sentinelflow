# SentinelFlow security threat model

Scope: CI/CD and Kubernetes software delivery. The developer PR, third-party Actions and base images, registries, and runtime workloads are treated as separate trust domains.

| Threat | Impact | Defense | Verification |
|---|---|---|---|
| Secret committed | Cloud/account compromise | Gitleaks history scan, secret rotation runbook | Synthetic lab fixture triggers gate |
| Malicious code introduced | Data exposure or arbitrary execution | Review + Semgrep + tests | SAST test case and PR review |
| Vulnerable package / base image | Exploitable runtime dependency | Trivy severity gate + frequent rebuilds | CVE report, patched digest |
| Workflow permission escalation | Registry/cloud credential theft | Read-only CI token, release OIDC identity constraints | Validate denied PR access |
| IaC misconfiguration | Privileged pod or lateral movement | Checkov + Kubernetes admission policies | Invalid fixture denied |
| Mutable image tag replaced | Unsigned code shipped | Digest pin + Cosign + provenance | Signature and digest negative test |
| Tampered GitOps manifest | Unapproved deployment | Protected GitOps repo, Argo scope, Kyverno | Attempt rejected manifest |
| RCE in a runtime container | Lateral movement | Nonroot, no token, no capabilities, policy-restricted network | K8s admission and network tests |

Residual risks: scanner blind spots, 0-days, CI SaaS trust, malicious maintainers, dependency update attacks, registry compromise, and incomplete network isolation. A passing pipeline is not a security guarantee.
