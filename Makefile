.PHONY: clean clean-work format format-check lint flake8 docstrings typecheck metrics security test check ci build check-dist publish-test publish

PYTHON_FILES := src tests scripts

clean-work:
	@mkdir -p work
	@find work -mindepth 1 ! -name .gitkeep -exec rm -rf {} +

clean: clean-work

format format-check lint flake8 docstrings typecheck metrics security test check ci build check-dist publish-test publish: clean-work

format:
	@uv run ruff format $(PYTHON_FILES)

format-check:
	@uv run ruff format --check $(PYTHON_FILES)

lint:
	@uv run ruff check $(PYTHON_FILES)

flake8:
	@uv run flake8 $(PYTHON_FILES)

docstrings:
	@uv run python scripts/check_docstrings.py

typecheck:
	@uv run mypy src tests scripts

metrics:
	@uv run python scripts/code_metrics.py

security:
	@uv run bandit -c pyproject.toml -r src scripts
	@bash scripts/security_deps.sh

test:
	@uv run pytest

check:
	@bash scripts/check.sh

ci:
	@bash scripts/check.sh --ci

build:
	@bash scripts/publish.sh build

check-dist:
	@bash scripts/publish.sh check-dist

publish-test:
	@bash scripts/publish.sh publish-test

publish:
	@bash scripts/publish.sh publish
