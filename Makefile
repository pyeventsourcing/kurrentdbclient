.EXPORT_ALL_VARIABLES:

# SHELL = bash

# EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore-ce/eventstoredb-ce:22.10.4-jammy
# EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore-ce/eventstoredb-ce:23.10.0-jammy
# EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore-ce/eventstoredb-oss:24.6.0-jammy
EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore/eventstoredb-ee:24.10.0-x64-8.0-bookworm-slim
# EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore-ce/eventstoredb-ce:24.2.0-alpha.115-jammy
# EVENTSTORE_DOCKER_IMAGE ?= docker.eventstore.com/eventstore-staging-ce/eventstoredb-ce:24.6.0-nightly-x64-8.0-jammy


POETRY ?= poetry
POETRY_VERSION=1.5.1
POETRY_INSTALLER_URL ?= https://install.python-poetry.org
PYTHONUNBUFFERED=1
SAMPLES_LINE_LENGTH=70

.PHONY: install-poetry
install-poetry:
	@curl -sSL $(POETRY_INSTALLER_URL) | python3
	$(POETRY) --version

.PHONY: install-packages
install-packages:
	$(POETRY) --version
	$(POETRY) install --no-root -vv $(opts)

.PHONY: install
install:
	$(POETRY) --version
	$(POETRY) install -vv $(opts)

.PHONY: install-pre-commit-hooks
install-pre-commit-hooks:
ifeq ($(opts),)
	$(POETRY) run pre-commit install
endif

.PHONY: uninstall-pre-commit-hooks
uninstall-pre-commit-hooks:
ifeq ($(opts),)
	$(POETRY) run pre-commit uninstall
endif

.PHONY: lock-packages
lock-packages:
	$(POETRY) lock -vv --no-update

.PHONY: update-packages
update-packages:
	$(POETRY) update -vv

.PHONY: lint-black
lint-black:
	$(POETRY) run black --check --diff --extend-exclude samples .
	$(POETRY) run black --check --diff --line-length=$(SAMPLES_LINE_LENGTH) ./samples

.PHONY: lint-flake8
lint-flake8:
	$(POETRY) run flake8

.PHONY: lint-isort
lint-isort:
	$(POETRY) run isort --check-only --diff --extend-skip-glob samples .
	$(POETRY) run isort --check-only --diff --line-length=$(SAMPLES_LINE_LENGTH) samples

.PHONY: lint-mypy
lint-mypy:
	$(POETRY) run mypy --strict

.PHONY: lint-python
lint-python: lint-black lint-flake8 lint-isort lint-mypy

.PHONY: lint
lint: lint-python

.PHONY: fmt-black
fmt-black:
	$(POETRY) run black --extend-exclude=samples .
	$(POETRY) run black --line-length=$(SAMPLES_LINE_LENGTH) ./samples

.PHONY: fmt-isort
fmt-isort:
	$(POETRY) run isort --extend-skip=samples .
	$(POETRY) run isort --line-length=$(SAMPLES_LINE_LENGTH) samples

.PHONY: fmt
fmt: fmt-isort fmt-black

.PHONY: test
test:
	@timeout --preserve-status --kill-after=10s 10m $(POETRY) run coverage run -m unittest discover ./tests -v
	$(POETRY) run coverage report --fail-under=100 --show-missing

# 	$(POETRY) run python -m pytest -v $(opts) $(call tests,.) & read -t 1 ||

# 	$(POETRY) run python -m pytest -v tests/test_docs.py
# 	$(POETRY) run python -m unittest discover tests -v

.PHONY: benchmark
benchmark:
	$(POETRY) run python tests/benchmark.py

.PHONY: build
build:
	$(POETRY) build
# 	$(POETRY) build -f sdist    # build source distribution only

.PHONY: publish
publish:
	$(POETRY) publish

# Orig proto files: https://github.com/EventStore/EventStore/tree/master/src/Protos/Grpc
.PHONY: grpc-stubs
grpc-stubs:
	$(POETRY) run python -m grpc_tools.protoc \
	  --proto_path=./protos \
	  --python_out=. \
	  --grpc_python_out=. \
	  --mypy_out=. \
	  protos/kurrentdbclient/protos/Grpc/code.proto     \
	  protos/kurrentdbclient/protos/Grpc/shared.proto   \
	  protos/kurrentdbclient/protos/Grpc/status.proto   \
	  protos/kurrentdbclient/protos/Grpc/streams.proto  \
	  protos/kurrentdbclient/protos/Grpc/persistent.proto \
	  protos/kurrentdbclient/protos/Grpc/gossip.proto \
	  protos/kurrentdbclient/protos/Grpc/cluster.proto \
	  protos/kurrentdbclient/protos/Grpc/projections.proto

.PHONY: start-kurrentdb-insecure
start-kurrentdb-insecure:
	@docker run -d -i -t -p 2113:2113 \
    --env "EVENTSTORE_ADVERTISE_HOST_TO_CLIENT_AS=localhost" \
    --env "EVENTSTORE_ADVERTISE_HTTP_PORT_TO_CLIENT_AS=2113" \
    --env "EVENTSTORE_RUN_PROJECTIONS=All" \
    --env "EVENTSTORE_START_STANDARD_PROJECTIONS=true" \
    --env "EVENTSTORE_ENABLE_ATOM_PUB_OVER_HTTP=true" \
    --name my-kurrentdb-insecure \
    $(EVENTSTORE_DOCKER_IMAGE) \
    --insecure

.PHONY: start-kurrentdb-secure
start-kurrentdb-secure:
	@docker run -d -i -t -p 2114:2113 \
    --env "HOME=/tmp" \
    --env "EVENTSTORE_ADVERTISE_HOST_TO_CLIENT_AS=localhost" \
    --env "EVENTSTORE_ADVERTISE_HTTP_PORT_TO_CLIENT_AS=2114" \
    --env "EVENTSTORE_RUN_PROJECTIONS=All" \
    --env "EVENTSTORE_START_STANDARD_PROJECTIONS=true" \
    --name my-kurrentdb-secure \
    $(EVENTSTORE_DOCKER_IMAGE) \
    --dev

.PHONY: attach-kurrentdb-insecure
attach-kurrentdb-insecure:
	@docker exec -it my-kurrentdb-insecure /bin/bash

.PHONY: attach-kurrentdb-secure
attach-kurrentdb-secure:
	@docker exec -it my-kurrentdb-secure /bin/bash

.PHONY: stop-kurrentdb-insecure
stop-kurrentdb-insecure:
	@docker stop my-kurrentdb-insecure
	@docker rm my-kurrentdb-insecure

.PHONY: stop-kurrentdb-secure
stop-kurrentdb-secure:
	@docker stop my-kurrentdb-secure
	@docker rm my-kurrentdb-secure

.PHONY: start-kurrentdb
start-kurrentdb: start-kurrentdb-insecure start-kurrentdb-secure docker-up

.PHONY: stop-kurrentdb
stop-kurrentdb: stop-kurrentdb-insecure stop-kurrentdb-secure docker-down

.PHONY: docker-pull
docker-pull:
	@docker compose pull

.PHONY: docker-build
docker-build:
	@docker compose build

.PHONY: docker-up
docker-up:
	@docker --version
	@docker compose up -d
	@echo "Waiting for containers to be healthy"
	@until docker compose ps | grep -in "healthy" | wc -l | grep -in 3 > /dev/null; do printf "." && sleep 1; done; echo ""
	@docker compose ps
	@sleep 15

.PHONY: docker-stop
docker-stop:
	@docker compose stop

.PHONY: docker-down
docker-down:
	@docker compose down -v --remove-orphans


.PHONY: docker-logs
docker-logs:
	@docker compose logs --follow --tail=1000


# Jaeger natively supports OTLP to receive trace data. You can run Jaeger in a docker container
# with the UI accessible on port 16686 and OTLP enabled on ports 4317 and 4318.
# https://opentelemetry.io/docs/languages/python/exporters/#jaeger
.PHONY: start-jaeger
start-jaeger:
	@docker run -d \
    -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
    -p 16686:16686 \
    -p 4317:4317 \
    -p 4318:4318 \
    -p 9411:9411 \
    --name jaeger \
    jaegertracing/all-in-one:latest

.PHONY: stop-jaeger
stop-jaeger:
	@docker stop jaeger
	@docker rm jaeger
