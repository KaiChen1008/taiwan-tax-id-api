# Taiwan Tax ID (UBN) Lookup API

A high-performance FastAPI service that provides a searchable interface for the Taiwan Government's Open Data on business registrations. It allows looking up Unified Business Numbers (UBN/統一編號) using business names.

## Features

- **High Performance:** Loads the ~300MB dataset into an optimized in-memory map for sub-millisecond lookups.
- **Auto-Updating:** Automatically downloads the latest `data.csv` from the [Government EIP](https://eip.fia.gov.tw/data/BGMOPEN1.csv) on startup and updates it daily at 04:00 (Taiwan Time).
- **Dockerized:** Ready for deployment with Docker and Docker Compose.
- **Modern Stack:** Built with Python 3.13, FastAPI, Pandas, and `uv`.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (Recommended) or Python 3.13+
- Docker & Docker Compose (for containerized deployment)

## Getting Started

### Local Development

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the API:**
   ```bash
   make run
   # OR
   uv run uvicorn main:app --reload
   ```

The server will start at `http://localhost:8000`. On the first run, it will automatically download the `data.csv` file (~300MB).

### Using Docker

The project is configured to mount the data as a volume, keeping the image size small.

```bash
# Build and start the container
make up

# Check logs to see download/load progress
docker logs -f tax-id-api
```

## API Usage

### Root
`GET /`
Returns a welcome message.

### Lookup UBN
`GET /get_ubn?name={BUSINESS_NAME}`

**Example Request:**
`GET http://localhost:8000/get_ubn?name=台積電`

**Example Response:**
```json
["23570644"]
```

*Note: If multiple UBNs are associated with the same name, the API returns a list containing all of them.*

## Project Structure

- `main.py`: Core API logic, data downloading, and scheduling.
- `data.csv`: The local cache of the government dataset (ignored by git).
- `pyproject.toml` / `uv.lock`: Dependency management.
- `Makefile`: Shortcuts for common development tasks.
- `GEMINI.md`: Detailed architectural context for AI assistants.

## Development

### Quality Gates
Before contributing, ensure:
1. `uv lock` is updated.
2. `ruff check .` passes (Linting).
3. `ruff format .` is applied (Formatting).

## License
MIT
