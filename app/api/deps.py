from __future__ import annotations

from collections.abc import Generator

from fastapi import Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DomainError
from app.db.session import get_db


def db_dep() -> Generator[Session, None, None]:
    yield from get_db()


def admin_key_dep(x_admin_key: str | None = Header(default=None)) -> None:
    if not settings.admin_api_key:
        return
    if x_admin_key != settings.admin_api_key:
        raise DomainError("Invalid admin API key", status_code=401)
