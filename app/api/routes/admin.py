from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import admin_key_dep, db_dep
from app.schemas.admin import ReindexRequest, ReindexResponse
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reindex", response_model=ReindexResponse, dependencies=[Depends(admin_key_dep)])
def reindex(payload: ReindexRequest, db: Session = Depends(db_dep)) -> ReindexResponse:
    stats = AdminService(db).reindex(payload)
    versions = [item.version for item in stats]
    msg = "; ".join(
        (
            f"v{item.version}: official_docs={item.official_documents}, "
            f"supplementary_docs={item.supplementary_documents}, chunks={item.indexed_chunks}"
        )
        for item in stats
    )
    return ReindexResponse(started=True, versions=versions, message=msg)
