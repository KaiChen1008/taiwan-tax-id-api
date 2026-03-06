# GEMINI.md - Taiwan Tax ID API Context

This document provides architectural and operational context for the `taiwan-tax-id-api` project.

## 1. Project Overview

The **Taiwan Tax ID API** is a FastAPI-based service designed to lookup Unified Business Numbers (UBN/統一編號) by business name. It processes a large dataset (~300MB CSV) provided by the Taiwan government and includes a Google Sheets integration.

### Core Technologies
- **Backend:** Python 3.13+, FastAPI, Pandas, Pydantic Settings, APScheduler, HTTPX.
- **Frontend:** Google Apps Script (JavaScript), managed via `clasp`.
- **Dependency Management:** `uv` (Python), `npm` (clasp).
- **Deployment:** Docker & Docker Compose.

### Architecture
- **Data Persistence:** The source data is stored in `data.csv`. This file is **not** included in the Docker image; it is mounted as a volume.
- **Data Lifecycle:** 
  - On startup, the application checks if `settings.DATA_FILE` exists. If not, it downloads it from `settings.DATA_URL`.
  - It then loads the CSV into memory (a dictionary mapping names to lists of UBNs) for fast lookups.
  - A background task runs daily at 04:00 (Taiwan Time) to download the latest CSV and reload the in-memory map.
- **Lookup Logic:** Exact name matching. If multiple UBNs exist for a single name, all are returned as a list of strings.
- **Frontend Integration:** A Google Apps Script client allows users to call the API directly from a spreadsheet using custom formulas or a batch lookup menu.

## 2. Project Structure

```text
.
├── app/                # Backend FastAPI application
│   ├── config.py       # Configuration and Pydantic settings
│   ├── data_manager.py # Logic for downloading and indexing the 300MB CSV
│   ├── main.py         # API routes and lifespan management
│   └── scheduler.py    # Background task for daily data updates
├── frontend/           # Google Apps Script integration
│   ├── .clasp.json     # Clasp configuration for deployment
│   ├── formula.js      # Custom =GET_TAX_ID() formula
│   └── main.js         # Batch processing and UI menu logic
├── data.csv            # The government dataset (ignored by git)
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Volume configuration for data persistence
└── Makefile            # Common dev tasks (run, up, down)
```

## 3. Development Conventions

### Code Style & Linting
- All comments and documentation must be in **English**.
- **Backend:** Uses `ruff` for linting and formatting (defined in `pyproject.toml`).
- **Frontend:** Follows standard Google Apps Script conventions.

### Environment Configuration
- Configuration is managed via `pydantic-settings` and a `.env` file.
- `DATA_URL`: The source URL for the government CSV.
- `DATA_FILE`: The local filename for the CSV (defaults to `data.csv`).

### Data Handling
- **Crucial:** `data.csv` is large (~300MB). Never commit it to git.
- The CSV has a metadata line on the second row which is skipped during loading (`skiprows=[1]`).

## 4. API Endpoints

- `GET /`: Root message and service status.
- `GET /get_ubn?name={NAME}`: Returns a list of UBNs for the given business name.
  - Returns `404` if the name is not found.

## 5. Quality Gates

- `uv lock` must be executed before commits.
- `ruff check .` and `ruff format . --check` should pass.
- **Frontend:** Ensure `clasp push` is successful after changes to the `frontend/` directory.
- Use mocking for `download_data` and external API calls in tests.
