.PHONY: help install dev-install install-stt test lint format clean run docs

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort

## Install the package in development mode
dev-install:
	@echo "${GREEN}Installing in development mode...${RESET}"
	pip install -e .

## Install production dependencies
install:
	@echo "${GREEN}Installing production dependencies...${RESET}"
	pip install .

## Install STT dependencies
install-stt:
	@echo "${GREEN}Installing STT dependencies...${RESET}"
	pip install -e ".[stt]"

## Install development dependencies
install-dev:
	@echo "${GREEN}Installing development dependencies...${RESET}"
	pip install -e ".[dev]"

## Run tests
test:
	@echo "${GREEN}Running tests...${RESET}"
	pytest tests/

## Run linter
lint:
	@echo "${GREEN}Running linter...${RESET}"
	flake8 dockevos/ tests/

## Format code
format:
	@echo "${GREEN}Formatting code...${RESET}"
	black dockevos/ tests/

## Clean build artifacts
clean:
	@echo "${GREEN}Cleaning build artifacts...${RESET}"
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

## Run the application
run:
	@echo "${GREEN}Starting Dockevos...${RESET}"
	python -m dockevos

## Build documentation
docs:
	@echo "${GREEN}Building documentation...${RESET}"
	# Add documentation build commands here

## Show system information
info:
	@echo "${GREEN}System information:${RESET}"
	@echo "Python: $(shell which python3) (${YELLOW}$(shell python3 --version 2>&1 | cut -d ' ' -f2)${RESET})"
	@echo "Pip: ${YELLOW}$(shell pip --version | cut -d ' ' -f2)${RESET}"
	@echo "Docker: ${YELLOW}$(shell docker --version 2>/dev/null || echo 'Not installed')${RESET}"
	@echo "Vosk Model: ${YELLOW}$(ls -d ~/.cache/vosk/models/* 2>/dev/null || echo 'Not downloaded')${RESET}"

## Show help (default)
.DEFAULT_GOAL := help
