from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.repositories.versions import VersionRepository
from app.schemas.version import VersionOut, VersionsResponse

router = APIRouter(prefix="/versions", tags=["versions"])


@router.get("", response_model=VersionsResponse)
def list_versions(db: Session = Depends(db_dep)) -> VersionsResponse:
    rows = VersionRepository(db).list_supported()
    return VersionsResponse(
        versions=[
            VersionOut(
                id=row.id,
                major_version=row.major_version,
                docs_base_url=row.docs_base_url,
                is_supported=row.is_supported,
                loaded_at=row.loaded_at,
            )
            for row in rows
        ]
    )
