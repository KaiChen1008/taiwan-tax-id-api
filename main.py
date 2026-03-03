import logging
import os
from urllib.parse import unquote
from contextlib import asynccontextmanager
from typing import Dict, List

import httpx
import pandas as pd
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    DATA_URL: str = "https://eip.fia.gov.tw/data/BGMOPEN1.csv"
    DATA_FILE: str = "data.csv"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Global variable to store data
# Structure: { "Business Name": ["UBN1", "UBN2"] }
name_to_ubn_map: Dict[str, List[str]] = {}


async def download_data():
    logger.info(f"Downloading data from {settings.DATA_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.DATA_URL, timeout=None)
            response.raise_for_status()
            with open(settings.DATA_FILE, "wb") as f:
                f.write(response.content)
        logger.info(f"Download complete, saved to {settings.DATA_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        return False


async def load_data():
    global name_to_ubn_map
    if not os.path.exists(settings.DATA_FILE):
        logger.info(f"{settings.DATA_FILE} does not exist, starting download...")
        success = await download_data()
        if not success:
            logger.error("Initial data download failed, cannot start service.")
            return

    logger.info(f"Loading {settings.DATA_FILE} (~300MB), please wait...")
    try:
        # Read required columns
        df = pd.read_csv(
            settings.DATA_FILE,
            usecols=["營業人名稱", "統一編號"],
            skiprows=[1],  # Skip the second row (index 1) which contains metadata
            dtype={"統一編號": str, "營業人名稱": str},
        )

        # Remove NaN values to avoid errors during processing
        df = df.dropna(subset=["營業人名稱", "統一編號"])

        # Use groupby to quickly create a dictionary mapping names to UBN lists
        new_map = df.groupby("營業人名稱")["統一編號"].apply(list).to_dict()
        name_to_ubn_map = new_map  # type: ignore
        logger.info(f"Loading complete, {len(name_to_ubn_map)} unique names found.")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")


async def scheduled_update():
    logger.info("Executing daily scheduled update...")
    if await download_data():
        await load_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await load_data()
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

    client_ip = request.client.host  # type: ignore
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
    ubns = name_to_ubn_map.get(name)
    if not ubns:
        raise HTTPException(
            status_code=404, detail="UBN not found for the given business name"
        )
    return ubns


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
