.PHONY: dep build clean help

dep: ## Install dependencies
	python -m pip install build pytest

test: ## Run tests
	python -m pytest

build: ## Build the project
	python -m build

clean: ## Clean the build artifacts
	rm -rf ./dist

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
