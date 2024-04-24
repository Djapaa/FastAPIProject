from pathlib import Path
import os
from typing import Any

from pydantic import (
    AliasChoices,
    AmqpDsn,
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
    RedisDsn, field_validator,
)

from dotenv import load_dotenv
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings

load_dotenv()



class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_NAME: str
    DB_HOST: str
    DB_PASS: str
    DB_PORT: int
    DB_USER: str
    ASYNC_DATABASE_URI: PostgresDsn | str = ""
    ECHO: bool

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        """
            Строим DSN по переменным из .env.
            Если в .env есть переменная ASYNC_DATABASE_URI, берем ее из .env
        """
        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DB_USER"],
                    password=info.data["DB_PASS"],
                    host=info.data["DB_HOST"],
                    port=info.data["DB_PORT"],
                    path=info.data["DB_NAME"],
                )
        return v

    TEST_DB_NAME: str
    TEST_DB_HOST: str
    TEST_DB_PASS: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    ASYNC_TEST_DATABASE_URI: PostgresDsn | str = ""

    @field_validator("ASYNC_TEST_DATABASE_URI", mode="after")
    def assemble_test_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["TEST_DB_USER"],
                    password=info.data["TEST_DB_PASS"],
                    host=info.data["TEST_DB_HOST"],
                    port=info.data["TEST_DB_PORT"],
                    path=info.data["TEST_DB_NAME"],
                )
        return v

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_HOST: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool


    DOMAIN_NAME: str

    MEDIA_ROOT: str
    MEDIA_URL: str


settings = Settings()
