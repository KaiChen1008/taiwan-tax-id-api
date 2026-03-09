import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    DATA_URL: str = "https://eip.fia.gov.tw/data/BGMOPEN1.csv"
    DATA_FILE: str = "data.csv"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
