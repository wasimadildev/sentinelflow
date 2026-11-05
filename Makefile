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
