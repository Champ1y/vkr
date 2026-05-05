from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.core.exceptions import DomainError
from app.schemas.ask import AskRequest, AskResponse
from app.services.orchestration import AskOrchestrationService

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse, response_model_exclude_none=True)
def ask(payload: AskRequest, db: Session = Depends(db_dep)) -> AskResponse:
    try:
        service = AskOrchestrationService(db)
    except RuntimeError as exc:
        raise DomainError(str(exc), status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc
    return service.handle_ask(payload)
