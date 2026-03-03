APP_NAME = main:app
UVICORN = uvicorn
HOST = 0.0.0.0
PORT = 8000

.PHONY: run build up down clean help

# run the FastAPI application locally
run:
	$(UVICORN) $(APP_NAME) --host $(HOST) --port $(PORT) --reload

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

# remove Python build artifacts and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	@echo "Cleanup completed."
