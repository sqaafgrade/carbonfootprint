.PHONY: install test cov lint fmt audit ci docker-run

install:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

test:
	cd backend && pytest -v
	cd frontend && npm test

cov:
	cd backend && pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	cd backend && ruff check . && mypy app/
	cd frontend && npm run lint

fmt:
	cd backend && ruff format .
	cd frontend && npx prettier --write src

audit:
	cd backend && pip-audit -r requirements.txt
	cd backend && bandit -r app/

ci: lint test audit

docker-run:
	docker build -t carbon-platform .
	docker run -p 8080:8080 -e USE_GEMINI=false -e USE_FIRESTORE=false -e USE_BIGQUERY=false -e USE_PUBSUB=false carbon-platform
