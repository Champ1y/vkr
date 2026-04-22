from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.history import QueryHistoryResponse
from app.services.history import HistoryService

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=QueryHistoryResponse)
def get_history(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(db_dep)) -> QueryHistoryResponse:
    return HistoryService(db).get_history(limit=limit)
