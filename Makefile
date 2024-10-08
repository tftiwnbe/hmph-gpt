VENV = venv
PYTHON = $(VENV)/bin/python
REQUIREMENTS = requirements.dev.txt

# Create venv if don't exists
venv:
	@if [ ! -d $(VENV) ]; then \
		echo "Creating venv..."; \
		python3 -m venv $(VENV); \
	fi

# Install requirements
install: venv
	@echo "Requirements installing..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(REQUIREMENTS)

# Run the bot
run: install
	@echo "Running the bot..."
	$(PYTHON) bot

# Run the bot and restart on Python file changes
watch: install
	@echo "Running in watch mode..."
	$(VENV)/bin/watchmedo auto-restart --patterns="*.py" --recursive -- $(PYTHON) bot

# Build and start container
build:
	@echo "Building container..."
	docker-compose up --build -d

# Stop container
stop:
	@echo "Stoping container..."
	docker-compose down

# Start tests with pytest
test: install
	@echo "Testing..."
	$(PYTHON) -m pytest

# Clean up venv
clean:
	@echo "Deleting venv..."
	rm -rf $(VENV)

# Recreate venv
reinstall: clean venv install
	@echo "Venv recreated."
