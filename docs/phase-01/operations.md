# Operations runbook

## Security gate fails

1. Read the failing job logs, identify commit and specific finding.
2. Reproduce with the local tool or a temporary non-sensitive test branch.
3. Patch code, IaC, package version, or base image; push updated PR.
4. Do not bypass an issue by adding broad ignore rules. For false positives, document the evidence and request reviewer approval.
5. Rotate any exposed credential; deleting it from a branch is not sufficient if it exists in Git history.

## Image CVE gate fails

- Rebuild against a patched, reviewed base digest; rescan.
- Check if affected package is exploitable in the actual container.
- If a fix is unavailable, document time-bound exception and acceptance owner. The Phase-1 pipeline ignores unfixed CVEs, which must be reviewed for production.

## CI pipeline is unexpectedly red

- Inspect the action release and GitHub runner compatibility.
- Confirm registry, tool download, and vulnerability database access.
- Check the Scan job's tool exit code; infrastructure failures are not passing scans.

## Emergency rollback (after GitOps phase)

- Revert the protected environment overlay to previous known-good signed image digest; open an incident ticket and follow the approval process.
- Verify image identity and deployment health; preserve event and audit evidence.

## Teardown

- Phase 1: `docker image rm sentinelflow-api:phase1` and stop local processes; no AWS resources created.
- Later phases: follow Terraform destroy runbook and verify billable resources (EKS, NAT, load balancers, logs, ECR) are removed.
