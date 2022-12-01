.ONESHELL:
VENV_NAME=env
VENV=$(VENV_NAME)/bin/

.PHONY: create-env
create-env: 			## Create environment and install pre-commits
	@echo "Creating an virtual env"
	@python3 -m venv $(VENV_NAME)

	@echo "Installing pre-commit hooks"
	@$(VENV)pip3 install pre-commit black isort flake8 pyproject-flake8 pytest
	@$(VENV)pre-commit install-hooks

.PHONY: install-requirements
install-requirements:		## Install and update requirements
	@echo "Installing requirements"
	@$(VENV)pip3 install -r requirements.txt

.PHONY: lint
lint:				## Lint code using pre-commits
	@$(VENV)pre-commit run -a

.PHONY: test
test:				## Run tests
	@$(VENV)pytest

.PHONY: help
help:            		## Show the help
	@echo "TARGETS\n"
	@fgrep "##" Makefile | fgrep -v fgrep
