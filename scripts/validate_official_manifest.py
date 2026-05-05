#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HTML_ROOT = PROJECT_ROOT / "corpus" / "postgres" / "html"
SUPPORTED_VERSIONS = ("16", "17", "18")
EXPECTED_LICENSE = "PostgreSQL License"
EXPECTED_LICENSE_URL = "https://www.postgresql.org/about/licence/"
REQUIRED_FIELDS = {
    "corpus_type",
    "pg_major_version",
    "language",
    "source_url",
    "local_path",
    "title",
    "status",
    "http_status",
    "content_hash",
    "downloaded_at",
    "manifest_updated_at",
    "license",
    "license_url",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def parse_iso_utc(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_version_manifest(version: str, errors: list[str]) -> int:
    version_root = OFFICIAL_HTML_ROOT / version
    manifest_path = version_root / "download_manifest.jsonl"

    if not manifest_path.exists():
        errors.append(f"Missing manifest: {manifest_path}")
        return 0

    html_files = sorted(
        p for p in version_root.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}
    )
    expected_local_paths = {
        f.resolve().relative_to(PROJECT_ROOT).as_posix(): f for f in html_files
    }

    rows_count = 0
    seen_local_paths: set[str] = set()

    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue

        rows_count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {manifest_path}:{line_no}: {exc}")
            continue

        missing_fields = sorted(REQUIRED_FIELDS - row.keys())
        if missing_fields:
            errors.append(
                f"Missing required fields in {manifest_path}:{line_no}: {', '.join(missing_fields)}"
            )
            continue

        if row.get("corpus_type") != "official":
            errors.append(f"corpus_type must be 'official' in {manifest_path}:{line_no}")

        pg_major_version = str(row.get("pg_major_version", "")).strip()
        if pg_major_version != version:
            errors.append(
                f"pg_major_version mismatch in {manifest_path}:{line_no}: {pg_major_version!r} != {version!r}"
            )

        if row.get("language") != "en":
            errors.append(f"language must be 'en' in {manifest_path}:{line_no}")

        if row.get("license") != EXPECTED_LICENSE:
            errors.append(f"license mismatch in {manifest_path}:{line_no}")

        if row.get("license_url") != EXPECTED_LICENSE_URL:
            errors.append(f"license_url mismatch in {manifest_path}:{line_no}")

        source_url = str(row.get("source_url", "")).strip()
        if not source_url:
            errors.append(f"Missing source_url in {manifest_path}:{line_no}")
        else:
            if "/docs/current/" in source_url:
                errors.append(f"Floating current URL found in {manifest_path}:{line_no}: {source_url}")
            if f"/docs/{version}/" not in source_url:
                errors.append(
                    f"Wrong version URL in {manifest_path}:{line_no}: expected /docs/{version}/ in {source_url}"
                )

        local_path = str(row.get("local_path", "")).strip()
        if not local_path:
            errors.append(f"Missing local_path in {manifest_path}:{line_no}")
            continue

        local_file = Path(local_path)
        if local_file.is_absolute():
            errors.append(f"Absolute local_path in {manifest_path}:{line_no}: {local_path}")
            continue

        if local_path in seen_local_paths:
            errors.append(f"Duplicate local_path in {manifest_path}:{line_no}: {local_path}")
        seen_local_paths.add(local_path)

        resolved_file = PROJECT_ROOT / local_file
        if not resolved_file.exists():
            errors.append(f"Missing local file in {manifest_path}:{line_no}: {local_path}")
            continue

        try:
            resolved_file.relative_to(version_root)
        except ValueError:
            errors.append(
                f"local_path outside corpus/postgres/html/{version} in {manifest_path}:{line_no}: {local_path}"
            )

        if resolved_file.suffix.lower() not in {".html", ".htm"}:
            errors.append(f"local_path is not HTML/HTM in {manifest_path}:{line_no}: {local_path}")

        if not str(row.get("title", "")).strip():
            errors.append(f"Empty title in {manifest_path}:{line_no}")

        content_hash = str(row.get("content_hash", "")).strip()
        if not content_hash.startswith("sha256:"):
            errors.append(f"Invalid content_hash format in {manifest_path}:{line_no}: {content_hash}")
        else:
            actual_hash = sha256_file(resolved_file)
            if content_hash != actual_hash:
                errors.append(
                    f"content_hash mismatch in {manifest_path}:{line_no}: {content_hash} != {actual_hash}"
                )

        manifest_updated_at = str(row.get("manifest_updated_at", "")).strip()
        if not manifest_updated_at or not parse_iso_utc(manifest_updated_at):
            errors.append(
                f"Invalid manifest_updated_at in {manifest_path}:{line_no}: {manifest_updated_at!r}"
            )

        expected_source = (
            f"https://www.postgresql.org/docs/{version}/"
            f"{resolved_file.relative_to(version_root).as_posix()}"
        )
        if source_url and source_url != expected_source:
            errors.append(
                f"source_url does not match local_path in {manifest_path}:{line_no}: {source_url} != {expected_source}"
            )

    if rows_count != len(expected_local_paths):
        errors.append(
            f"Row count mismatch for version {version}: manifest rows={rows_count}, html files={len(expected_local_paths)}"
        )

    missing_paths = sorted(set(expected_local_paths.keys()) - seen_local_paths)
    if missing_paths:
        errors.append(
            f"Manifest missing {len(missing_paths)} HTML files for version {version}; first missing: {missing_paths[0]}"
        )

    unexpected_paths = sorted(seen_local_paths - set(expected_local_paths.keys()))
    if unexpected_paths:
        errors.append(
            f"Manifest contains {len(unexpected_paths)} unexpected paths for version {version}; first unexpected: {unexpected_paths[0]}"
        )

    return rows_count


def validate_manifests() -> int:
    if not OFFICIAL_HTML_ROOT.exists():
        print(f"ERROR: missing corpus root: {OFFICIAL_HTML_ROOT}")
        return 1

    errors: list[str] = []
    checked_rows = 0

    for version in SUPPORTED_VERSIONS:
        checked_rows += validate_version_manifest(version, errors)

    if errors:
        print("ERROR: official manifest validation failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("OK: official manifests are valid")
    print(f"Checked manifests: {len(SUPPORTED_VERSIONS)}")
    print(f"Checked rows: {checked_rows}")
    return 0


def main() -> None:
    sys.exit(validate_manifests())


if __name__ == "__main__":
    main()
