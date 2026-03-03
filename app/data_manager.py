import os
from typing import Dict, List

import httpx
import pandas as pd
from app.config import logger, settings

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
