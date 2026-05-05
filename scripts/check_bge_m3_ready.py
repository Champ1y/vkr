#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CheckResult:
    name: str
    ok: bool
    details: str
    skipped: bool = False


def _print_result(item: CheckResult) -> None:
    if item.skipped:
        prefix = "SKIP"
    else:
        prefix = "OK" if item.ok else "FAIL"
    print(f"[{prefix}] {item.name}: {item.details}")


def _run_corpus_validator(repo_root: Path) -> CheckResult:
    cmd = [
        sys.executable,
        "corpus/tutorial/scripts/validate_corpus_before_embeddings.py",
        "--corpus-root",
        "corpus",
    ]
    try:
        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    except Exception as exc:  # pragma: no cover
        return CheckResult("corpus_validator", False, f"Не удалось запустить валидатор: {exc}")

    merged_output = f"{proc.stdout}\n{proc.stderr}".strip()
    ready_flag = "corpus_ready_for_chunking_and_embeddings = true"
    is_ready = ready_flag in merged_output.lower()

    details = f"returncode={proc.returncode}"
    if proc.returncode != 0:
        details += "; валидатор завершился с ошибкой"
    if not is_ready:
        details += "; флаг готовности не найден"

    if merged_output:
        print("--- corpus validator output ---")
        print(merged_output)
        print("--- end corpus validator output ---")

    return CheckResult("corpus_validator", proc.returncode == 0 and is_ready, details)


def _check_supplementary_path(repo_root: Path) -> CheckResult:
    from app.core.config import settings

    configured = settings.supplementary_path
    expected_rel = Path("corpus/tutorial")
    expected_abs = (repo_root / expected_rel).resolve()

    if configured.is_absolute():
        configured_abs = configured.resolve()
    else:
        configured_abs = (repo_root / configured).resolve()

    is_default = configured.as_posix() == expected_rel.as_posix()
    points_to_expected = configured_abs == expected_abs and expected_abs.exists()
    ok = is_default or points_to_expected

    return CheckResult(
        "supplementary_dir",
        ok,
        f"configured={configured} resolved={configured_abs} expected={expected_abs}",
    )


def _check_db_vector_state() -> tuple[bool, list[CheckResult]]:
    results: list[CheckResult] = []
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
    except Exception as exc:
        results.append(CheckResult("db_connection", False, f"DB не проверена: отсутствует SQLAlchemy ({exc})", skipped=True))
        results.append(CheckResult("db_vector_extension", False, "DB не проверена (dependency missing)", skipped=True))
        results.append(CheckResult("db_embedding_column", False, "DB не проверена (dependency missing)", skipped=True))
        return False, results

    try:
        from app.core.config import settings
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            has_vector = bool(conn.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='vector')")).scalar())
            results.append(CheckResult("db_vector_extension", has_vector, f"vector_extension_present={has_vector}"))

            try:
                row = conn.execute(
                    text(
                        """
                        SELECT atttypid::regtype::text AS type_name, atttypmod
                        FROM pg_attribute
                        WHERE attrelid='embeddings'::regclass
                          AND attname='embedding'
                          AND NOT attisdropped
                        LIMIT 1
                        """
                    )
                ).mappings().first()

                if not row:
                    results.append(CheckResult("db_embedding_column", False, "Не найдена колонка embeddings.embedding"))
                else:
                    typmod = int(row["atttypmod"])
                    dim = typmod if typmod > 4 else None
                    is_vector_1024 = row["type_name"] == "vector" and dim == 1024
                    results.append(
                        CheckResult(
                            "db_embedding_column",
                            is_vector_1024,
                            f"type={row['type_name']} atttypmod={typmod} inferred_dimension={dim}",
                        )
                    )
            except SQLAlchemyError as exc:
                results.append(CheckResult("db_embedding_column", False, f"Не удалось проверить колонку embeddings.embedding: {exc}"))

        engine.dispose()
        return True, results
    except SQLAlchemyError as exc:
        results.append(CheckResult("db_connection", False, f"DB не проверена: {exc}", skipped=True))
        results.append(CheckResult("db_vector_extension", False, "DB не проверена (connection failed)", skipped=True))
        results.append(CheckResult("db_embedding_column", False, "DB не проверена (connection failed)", skipped=True))
        return False, results


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    results: list[CheckResult] = []

    try:
        from app.core.config import settings
        from app.services.adapters.embeddings import EmbeddingServiceFactory
        from app.services.ingestion.supplementary_loader import SupplementaryCorpusLoader
    except Exception as exc:
        results.append(CheckResult("python_dependencies", False, f"Не удалось импортировать зависимости приложения: {exc}"))
        print("=== BGE-M3 preflight checks ===")
        for item in results:
            _print_result(item)
        print("DB_CHECKS_STATUS = not_checked")
        print("BGE_M3_READY_FOR_REINDEX = false")
        return 1

    results.append(
        CheckResult(
            "embedding_model",
            settings.embedding_model == "BAAI/bge-m3",
            f"configured={settings.embedding_model} expected=BAAI/bge-m3",
        )
    )
    results.append(
        CheckResult(
            "embedding_dimension",
            settings.embedding_dimension == 1024,
            f"configured={settings.embedding_dimension} expected=1024",
        )
    )
    results.append(_check_supplementary_path(repo_root))

    results.append(_run_corpus_validator(repo_root))

    db_checked, db_results = _check_db_vector_state()
    results.extend(db_results)

    try:
        embedding_service = EmbeddingServiceFactory.create()
        sample_vector = embedding_service.embed_text("test")
        sample_len = len(sample_vector)
        results.append(
            CheckResult(
                "sample_embedding_length",
                sample_len == 1024,
                f"provider={settings.embedding_provider} model={embedding_service.model_name} length={sample_len}",
            )
        )
    except Exception as exc:  # pragma: no cover - depends on runtime model cache/network
        results.append(CheckResult("sample_embedding_length", False, f"Не удалось получить sample embedding: {exc}"))

    try:
        docs = SupplementaryCorpusLoader().load_documents(version="16")
        count = len(docs)
        ok = count > 2
        details = f"loaded_docs_v16={count} expected_approx=129 (curated+processed_html)"
        if count <= 2:
            details += "; похоже загружается не тот corpus"
        results.append(CheckResult("supplementary_loader_count_v16", ok, details))
    except Exception as exc:
        results.append(CheckResult("supplementary_loader_count_v16", False, f"Ошибка загрузчика supplementary: {exc}"))

    print("=== BGE-M3 preflight checks ===")
    for item in results:
        _print_result(item)

    non_skipped_failures = [item for item in results if (not item.skipped and not item.ok)]
    if not db_checked:
        print("DB_CHECKS_STATUS = not_checked")
    else:
        print("DB_CHECKS_STATUS = checked")

    ready = len(non_skipped_failures) == 0 and db_checked
    print(f"BGE_M3_READY_FOR_REINDEX = {'true' if ready else 'false'}")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
