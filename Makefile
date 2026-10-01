ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
API := $(ROOT)/api
WEB := $(ROOT)/web
COMPOSE := docker compose -f "$(ROOT)/compose.yaml"
LOCAL_DB := postgresql+psycopg://postgres@127.0.0.1:55479/yupicture
UV := env APP_ENV=local DATABASE_URL="$(LOCAL_DB)" uv --directory "$(API)" run --frozen

.PHONY: install install-frozen browser-install db-up db-stop migrate test-api lint-api test-web typecheck build test-e2e test-mutation check dev-api dev-web

install:
	uv --directory "$(API)" sync --python 3.13
	pnpm --dir "$(WEB)" install
	pnpm --dir "$(WEB)" exec playwright install chromium

install-frozen:
	uv --directory "$(API)" sync --python 3.13 --frozen
	pnpm --dir "$(WEB)" install --frozen-lockfile

browser-install:
	pnpm --dir "$(WEB)" exec playwright install --with-deps chromium

db-up:
	$(COMPOSE) up -d --wait --wait-timeout 60 db

db-stop:
	$(COMPOSE) stop db

migrate:
	$(UV) alembic upgrade head

test-api:
	$(UV) pytest -q

lint-api:
	$(UV) ruff check .

test-web:
	pnpm --dir "$(WEB)" run test:unit

typecheck:
	pnpm --dir "$(WEB)" run typecheck

build:
	pnpm --dir "$(WEB)" run build

test-e2e:
	pnpm --dir "$(WEB)" run test:e2e

test-mutation:
	$(UV) pytest tests/test_health.py::test_readiness_rejects_unavailable_database -q
	$(UV) python -m tests.mutation_check
	$(UV) python -m tests.users_mutation_check

# Prerequisites: install-frozen and browser-install; check prepares the isolated DB.
check:
	$(MAKE) db-up
	$(MAKE) migrate
	$(MAKE) lint-api
	$(MAKE) test-api
	$(MAKE) test-web
	$(MAKE) typecheck
	$(MAKE) build
	$(MAKE) test-e2e
	$(MAKE) test-mutation

dev-api:
	$(UV) uvicorn app.main:app --host 127.0.0.1 --port 8009

dev-web:
	env API_BASE_URL="http://127.0.0.1:8009" pnpm --dir "$(WEB)" run dev
