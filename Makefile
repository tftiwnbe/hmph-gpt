# Settings
VENV = venv
PYTHON = $(VENV)/bin/python
REQUIREMENTS = requirements.dev.txt
MAIN = main.py
ALEMBIC = ../$(PYTHON) -m alembic
ALEMBIC_DIR = migrations
ENV_FILE = .env


.PHONY: venv install start watch build stop clean reinstall db-revision db-upgrade db-downgrade db-history db-current help

# Help target
help:
	@echo "Makefile commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make start         - Start the bot"
	@echo "  make watch         - Watch for changes and restart"
	@echo "  make build         - Build containers"
	@echo "  make stop          - Stop containers"
	@echo "  make clean         - Clean up the environment"
	@echo "  make reinstall     - Recreate the virtual environment"
	@echo "  make db-revision   - Create a new migration (pass name=<name>)"
	@echo "  make db-upgrade    - Apply migrations (pass target=<version>)"
	@echo "  make db-downgrade  - Rollback migrations (pass target=<version>)"
	@echo "  make db-history    - Show migration history"
	@echo "  make db-current    - Display the current database version"
	@echo "  make help          - Show this help message"


# Create venv if it doesn't exist
venv:
	@if [ ! -d $(VENV) ]; then \
		echo "Creating venv..."; \
		python3.13 -m venv $(VENV); \
	fi

# Cleanup environment
clean:
	@echo "Deleting venv..."
	@if [ -d $(VENV) ]; then rm -rf $(VENV); fi
	@if [ -d $(FRONTEND_DIR)/node_modules ]; then rm -rf $(FRONTEND_DIR)/node_modules; fi

# Install dependencies
install: venv
	@echo "Installing requirements..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@clear

# Recreate venv
reinstall: clean venv install
	@echo "Venv recreated."

# Start bot
start: install
	@echo "Starting bot..."
	@cd bot && ../$(PYTHON) $(MAIN)

# Watch for changes to restart
watch: install
	@echo "Running in watch mode..."
	@cd bot && ../$(VENV)/bin/watchmedo auto-restart --patterns="*.py" --recursive -- ../$(PYTHON) $(MAIN)

# Build and start container as daemon
build:
	@echo "Building container..."
	docker compose up --build

# Stop container
stop:
	@echo "Stopping container..."
	docker compose down

# Create a new migration
db-revision:
	@cd bot && $(ALEMBIC) -c $(ALEMBIC_DIR)/alembic.ini revision --autogenerate -m "$(name)"

# Apply migrations
db-upgrade:
	@cd bot && $(ALEMBIC) -c $(ALEMBIC_DIR)/alembic.ini upgrade $(target)

# Rollback migrations
db-downgrade:
	@cd bot && $(ALEMBIC) -c $(ALEMBIC_DIR)/alembic.ini downgrade $(target)

# Show migration history
db-history:
	@cd bot && $(ALEMBIC) -c $(ALEMBIC_DIR)/alembic.ini history

# Show current database version
db-current:
	@cd bot && $(ALEMBIC) -c $(ALEMBIC_DIR)/alembic.ini current
