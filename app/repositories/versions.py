from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Version


class VersionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_supported(self) -> list[Version]:
        stmt = select(Version).where(Version.is_supported.is_(True)).order_by(Version.major_version.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_major(self, major_version: str) -> Version | None:
        stmt = select(Version).where(Version.major_version == major_version)
        return self.db.scalar(stmt)

    def ensure_seed_versions(self, versions: list[str] | None = None) -> list[Version]:
        target_versions = versions or settings.supported_versions
        existing = {v.major_version: v for v in self.db.scalars(select(Version)).all()}
        created: list[Version] = []

        for version in target_versions:
            if version in existing:
                if not existing[version].is_supported:
                    existing[version].is_supported = True
                continue

            docs_base_url = f"{settings.official_docs_base_url.rstrip('/')}/{version}/"
            row = Version(major_version=version, docs_base_url=docs_base_url, is_supported=True)
            self.db.add(row)
            created.append(row)

        self.db.flush()
        self.db.commit()

        stmt = select(Version).where(Version.major_version.in_(target_versions)).order_by(Version.major_version.desc())
        return list(self.db.scalars(stmt).all())
