# Phase-1 validation record

Validation environment: Node.js v22.16.0 in the build workspace (November 5, 2026).

| Check | Result | Method |
|---|---|---|
| Unit tests | PASS | `make test`: 6/6 passed |
| Coverage run | PASS | `make coverage`: app.mjs line coverage 100% in local run |
| HTTP smoke tests | PASS | `make smoke`: /healthz, /readyz, /api/v1/info |
| Node syntax | PASS | `node --check` for app, server and tests |
| NPM lockfile install | PASS | `npm ci --ignore-scripts --no-audit --no-fund` |
| YAML structure | PASS | Parsed all K8s manifests and CI workflow with PyYAML |
| Docker image build | NOT RUN | Docker CLI/daemon unavailable in validation workspace |
| Checkov / Semgrep / Gitleaks / Trivy / Syft | NOT RUN | External scanners not available in validation workspace; CI workflows require first GitHub run |
| GitHub Actions | NOT RUN | Files are delivered as a new repository; no GitHub push has been performed |
| Kubernetes apply | NOT RUN | No kubectl/cluster available; deployment placeholder image must be replaced first |

This record is intentionally scoped. Passing local application tests does not prove that all external security scanners or deployment workflows will pass. Scan results must be confirmed on a real GitHub Actions run after the repository is pushed.
