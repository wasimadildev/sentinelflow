.PHONY: test coverage run docker-build docker-run smoke local-security

test:
	cd apps/api && npm test

coverage:
	cd apps/api && npm run test:coverage

run:
	cd apps/api && npm start

docker-build:
	docker build -f apps/api/Dockerfile -t sentinelflow-api:phase1 .

docker-run:
	docker run --rm \
		--read-only \
		--cap-drop ALL \
		--security-opt no-new-privileges \
		-p 127.0.0.1:8081:8080 \
		sentinelflow-api:phase1

smoke:
	bash scripts/smoke.sh

local-security:
	bash scripts/local-security.sh



.PHONY: phase2-test phase2-validate phase2-render phase2-verify
phase2-test:
	python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v

# Run after downloading an actual release artifact from GitHub Actions.
phase2-validate:
	python3 scripts/validate_sbom.py artifacts/sentinelflow-api.spdx.json
	python3 scripts/release_metadata.py verify --file artifacts/release.json

phase2-render:
	python3 scripts/render_release_overlay.py --release artifacts/release.json --output deploy/k8s/overlays/release/kustomization.yaml

phase2-verify:
	bash scripts/verify-release.sh artifacts/release.json
