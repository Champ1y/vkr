# BGE-M3 Migration and Full Reindex

## Target configuration

- `EMBEDDING_PROVIDER=local`
- `EMBEDDING_MODEL=BAAI/bge-m3`
- `EMBEDDING_DIMENSION=1024`
- `EMBEDDING_BATCH_SIZE=8`
- `EMBEDDING_MAX_SEQ_LENGTH=8192`
- `SUPPLEMENTARY_DIR=corpus/tutorial`

`BAAI/bge-m3` is used in dense mode only. Sparse/ColBERT retrieval is intentionally not enabled in this stage.

## Important notes

- Migration `20260504_0002_bge_m3_1024` is destructive for indexed corpus data.
- It truncates `documents` with `CASCADE`, which clears `documents/chunks/embeddings/query_sources`.
- After migration, a full reindex is required for official + supplementary corpora across versions `16 17 18`.

## Docker commands

```bash
docker compose down
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python scripts/check_bge_m3_ready.py
docker compose run --rm backend python -m app.cli.manage seed-versions
docker compose run --rm backend python -m app.cli.manage reindex \
  --versions 16 17 18 \
  --official \
  --supplementary \
  --batch-size 8 \
  --commit-every-docs 25 \
  --progress-every 10
```

Do not use `--max-pages` for final reindex.

## Post-reindex SQL checks

```sql
SELECT embedding_model, embedding_dimension, count(*)
FROM embeddings
GROUP BY embedding_model, embedding_dimension;

SELECT v.major_version, d.corpus_type, count(*) AS documents
FROM documents d
JOIN versions v ON v.id = d.version_id
GROUP BY v.major_version, d.corpus_type
ORDER BY v.major_version, d.corpus_type;

SELECT
  (SELECT count(*) FROM chunks) AS chunks_count,
  (SELECT count(*) FROM embeddings) AS embeddings_count;
```

Expected outcomes:

- `embedding_model = BAAI/bge-m3`
- `embedding_dimension = 1024`
- official and supplementary docs exist for each version `16/17/18`
- `chunks_count = embeddings_count`
