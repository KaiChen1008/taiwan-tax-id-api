from app.config import logger
from app.data_manager import download_data, load_data


async def scheduled_update():
    logger.info("Executing daily scheduled update...")
    if await download_data():
        await load_data()
