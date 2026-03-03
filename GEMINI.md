# GEMINI.md - Taiwan Tax ID API Context

This document provides architectural and operational context for the `taiwan-tax-id-api` project.

## Project Overview

The **Taiwan Tax ID API** is a FastAPI-based service designed to lookup Unified Business Numbers (UBN/統一編號) by business name. It processes a large dataset (~300MB CSV) provided by the Taiwan government.

### Core Technologies
- **Language:** Python 3.13+
- **Framework:** FastAPI
- **Data Processing:** Pandas
- **Scheduling:** APScheduler (for daily data updates)
- **HTTP Client:** HTTPX (for downloading the CSV)
- **Dependency Management:** `uv` (preferred) or `pip`
- **Deployment:** Docker & Docker Compose

### Architecture
- **Data Persistence:** The source data is stored in `data.csv`. This file is **not** included in the Docker image; it is mounted as a volume.
- **Data Lifecycle:** 
  - On startup, the application checks if `data.csv` exists. If not, it downloads it.
  - It then loads the CSV into memory (a dictionary mapping names to lists of UBNs) for fast lookups.
  - A background task (using `AsyncIOScheduler`) runs daily at 04:00 (Taiwan Time) to download the latest CSV from the government and reload the in-memory map.
- **Lookup Logic:** Exact name matching. If multiple UBNs exist for a single name, all are returned.

## Building and Running

### Local Development (using `uv`)
```bash
# Install dependencies
uv sync

# Run the application with hot-reload
uv run uvicorn main:app --reload
```

### Local Development (using `Makefile`)
```bash
# Run the application locally
make run
```

### Containerized Deployment
```bash
# Build and start the container in detached mode
make up

# Stop the container
make down
```

## Development Conventions

### Code Style & Linting
- The project uses `ruff` for linting and formatting (defined in `pyproject.toml`).
- Follow standard FastAPI patterns (e.g., using `lifespan` for startup/shutdown tasks).

### Environment Configuration
- The source data URL is hardcoded in `main.py` as `DATA_URL`.
- Port 8000 is the default for both local and containerized runs.

### Data Handling
- **Crucial:** `data.csv` is large (~300MB). Never commit it to git (it is in `.gitignore`).
- When modifying `Dockerfile`, ensure `data.csv` is **not** copied into the image; rely on volume mounting in `docker-compose.yml`.
- The CSV has a metadata line on the second row which is skipped during loading (`skiprows=[1]`).

## API Endpoints

- `GET /`: Root message.
- `GET /get_ubn?name={名称}`: Returns a list of UBNs for the given business name.
  - Returns `404` if the name is not found.

## 5. Quality Gates

- `uv lock` (or `uv sync`) must be executed before commits to ensure `uv.lock` is up-to-date.
- `ruff check .` and `ruff format . --check` should pass without errors.
- Unit tests with high coverage for API endpoints and the data mapping logic.
- Use mocking for `download_data` and external API calls in tests to isolate business logic from external dependencies.
