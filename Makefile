DEPS_MANAGER := uv
EXECUTOR := $(DEPS_MANAGER) run
LOGGING_CONFIG := conf/logging.dev.yaml
ENV ?= sb

.PHONY: all help docs lint format x lx fx lint-fix format-fix

help: ## Show this help.
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

docs:
	$(EXECUTOR) mkdocs serve

lint: ## Lint code with ruff
	$(EXECUTOR) ruff check $(ARGS)

format: ## Check formatting with ruff
	$(EXECUTOR) ruff format --check $(ARGS)

x: lx fx ## Fix lint and formatting (ruff)

lx: lint-fix
lint-fix:
	$(EXECUTOR) ruff check --fix $(ARGS)

fx: format-fix
format-fix:
	$(EXECUTOR) ruff format $(ARGS)
