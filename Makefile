UV = uv
APP = app.main:app

.PHONY: run up down clean help

# Run the API locally with hot-reload
run:
	$(UV) run uvicorn $(APP) --reload --no-access-log

# Start production containers
up:
	docker-compose up -d --build

# Stop containers
down:
	docker-compose down

# Clean build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
	find . -type f -name ".DS_Store" -delete
