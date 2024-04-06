from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

db_name = os.getenv("DB_NAME")


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_NAME: str
    DB_HOST: str
    DB_PASS: str
    DB_PORT: str
    DB_USER: str


settings = Settings()
