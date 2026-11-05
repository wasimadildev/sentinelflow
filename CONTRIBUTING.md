# Contributing to SentinelFlow

1. Create a feature branch, describe the security impact, and open a pull request.
2. Run `make test`, `make smoke`, and `make docker-build` before requesting review.
3. Do not commit `.env`, cloud access keys, vulnerability databases, or unredacted scan artifacts.
4. Wait for the required Security Gate; document fixes rather than weakening policies.
5. Request independent review for changes under `.github/workflows`, `security`, `deploy`, `infra`, or `gitops`.
6. Include a test that fails before a security fix and passes afterward when practical.
