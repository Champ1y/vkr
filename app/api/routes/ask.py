from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.ask import AskRequest, AskResponse
from app.services.orchestration import AskOrchestrationService

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse, response_model_exclude_none=True)
def ask(payload: AskRequest, db: Session = Depends(db_dep)) -> AskResponse:
    service = AskOrchestrationService(db)
    return service.handle_ask(payload)
