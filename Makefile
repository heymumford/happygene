.PHONY: help install dev-install lint type-check test test-unit test-chaos test-validation coverage clean build docs

PYTHON := python3
UV := uv
PYTEST := $(PYTHON) -m pytest

# Default target
help:
	@echo "HappyGene Development Targets"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make dev-install    Install with dev dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  make lint           Run ruff linter"
	@echo "  make type-check     Run mypy type checking"
	@echo "  make format         Auto-format with black + isort"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-chaos     Run chaos engineering tests"
	@echo "  make test-validation Run cross-tool validation tests"
	@echo "  make coverage       Run tests with coverage report"
	@echo ""
	@echo "Build & Docs:"
	@echo "  make build          Build Python package"
	@echo "  make docs           Build documentation"
	@echo "  make clean          Clean build artifacts"
	@echo ""
	@echo "Run:"
	@echo "  make run CONFIG=<file.yaml>   Run simulation from YAML config"

# Installation
install:
	$(PYTHON) -m pip install -e .

dev-install:
	$(PYTHON) -m pip install -e ".[dev,mcp,ui,science,docs]"

# Quality gates
lint:
	@echo "Running linter..."
	$(PYTHON) -m ruff check .

type-check:
	@echo "Running type checker..."
	$(PYTHON) -m mypy happygene

format:
	@echo "Auto-formatting code..."
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m ruff check --fix .

# Testing
test:
	@echo "Running all tests..."
	$(PYTEST)

test-unit:
	@echo "Running unit tests..."
	$(PYTEST) -m unit engine/tests/unit tests/unit

test-chaos:
	@echo "Running chaos engineering tests..."
	$(PYTEST) -m chaos engine/tests/chaos tests/chaos

test-validation:
	@echo "Running validation tests..."
	$(PYTEST) -m validation engine/tests/validation tests/validation

coverage:
	@echo "Running tests with coverage..."
	$(PYTEST) --cov=happygene --cov-report=html --cov-report=term-plus
	@echo "Coverage report: htmlcov/index.html"

# Build & Docs
build: lint type-check test
	@echo "Building package..."
	$(PYTHON) -m build

docs:
	@echo "Building documentation..."
	mkdocs build

docs-serve:
	@echo "Serving documentation locally..."
	mkdocs serve

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist htmlcov .coverage .mypy_cache .ruff_cache
	@echo "Clean complete"

# Run simulation
run:
	@if [ -z "$(CONFIG)" ]; then \
		echo "Usage: make run CONFIG=path/to/config.yaml"; \
		exit 1; \
	fi
	$(PYTHON) -m happygene.cli run $(CONFIG)

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -f docker/Dockerfile.sim -t happygene:latest .

docker-compose-up:
	@echo "Starting local dev stack..."
	docker-compose -f docker/docker-compose.yml up -d

docker-compose-down:
	@echo "Stopping local dev stack..."
	docker-compose -f docker/docker-compose.yml down

# Git hooks
install-hooks:
	@echo "Installing pre-push hooks..."
	mkdir -p .git/hooks
	cp changelog/scripts/pre-push-hook.sh .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "Hooks installed"

# Development workflow
dev: dev-install format lint type-check test
	@echo "✓ Development environment ready"

# Full quality gate (pre-commit)
quality: lint type-check test coverage
	@echo "✓ Quality gates passed"
