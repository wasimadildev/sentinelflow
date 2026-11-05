# Argo CD GitOps — Phase 4

Not installed in Phase 1. Production should use a separate protected GitOps repository, with review-protected environment overlays and immutable image digest references. Limit Argo service account RBAC to authorized namespaces, and verify Kyverno policy installation before rollout.
