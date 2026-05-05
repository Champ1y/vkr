# PGExercises manifest fix report

## Summary

- manifest: `/home/arz/Desktop/RAG_postgres/corpus/tutorial/html/pgexercises/manifest.jsonl`
- backup: `/home/arz/Desktop/RAG_postgres/corpus/tutorial/html/pgexercises/manifest.jsonl.bak.20260504T123117Z`
- known missing registry: `/home/arz/Desktop/RAG_postgres/corpus/tutorial/external_registry/known_missing_pgexercises_pages.json`
- total records: 61
- error records checked: 10
- fixed existing pages: 0
- known missing pages: 10
- remaining status:error: 0

## Result

Да, status:error в manifest устранён.

## Fixed records

- нет

## Known missing records

- `about.html` — https://pgexercises.com/about.html
- `questions/joins/threejoin.html` — https://pgexercises.com/questions/joins/threejoin.html
- `questions/date/extract.html` — https://pgexercises.com/questions/date/extract.html
- `questions/date/interval2.html` — https://pgexercises.com/questions/date/interval2.html
- `questions/string/substr.html` — https://pgexercises.com/questions/string/substr.html
- `questions/string/concat.html` — https://pgexercises.com/questions/string/concat.html
- `questions/recursive/getupward.html` — https://pgexercises.com/questions/recursive/getupward.html
- `questions/updates/updatecalculated.html` — https://pgexercises.com/questions/updates/updatecalculated.html
- `questions/updates/update.html` — https://pgexercises.com/questions/updates/update.html
- `questions/updates/delete.html` — https://pgexercises.com/questions/updates/delete.html

## Important

Этот скрипт не скачивал страницы из интернета, не менял HTML, не пересчитывал chunks и embeddings.
Если `known_missing_count > 0`, это не блокирует embeddings автоматически, но должно быть явно отражено в отчёте корпуса.
