from contextlib import asynccontextmanager
from urllib.parse import unquote

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Query, Request

from app.config import logger
from app import data_manager
from app.scheduler import scheduled_update


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await data_manager.load_data()
    scheduler = AsyncIOScheduler()
    # Daily update at 04:00 (Taiwan time)
    scheduler.add_job(scheduled_update, "cron", hour=4, minute=0)
    scheduler.start()
    yield
    # Shutdown logic
    scheduler.shutdown()


app = FastAPI(title="Taiwan Tax ID Lookup API", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    query = unquote(f"?{request.url.query}") if request.url.query else ""
    http_version = request.scope.get("http_version", "1.1")
    status_code = response.status_code

    logger.info(
        f'{client_ip} - "{method} {path}{query} HTTP/{http_version}" {status_code}'
    )

    return response


@app.get("/")
def read_root():
    return {"message": "Welcome to Taiwan Tax ID Lookup API. Use /get_ubn?name=NAME"}


@app.get("/get_ubn")
async def get_ubn(name: str = Query(..., description="Business name to lookup")):
    name = name.strip()
    ubns = data_manager.name_to_ubn_map.get(name)
    if not ubns:
        raise HTTPException(
            status_code=404, detail="UBN not found for the given business name"
        )
    return ubns


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8092, access_log=False)
