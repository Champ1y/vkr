# PGExercises Manifest Audit Report

- Total manifest rows: **61**
- Error rows fixed to downloaded (file exists): **1**
- Remaining missing pages (status=error): **10**

## Fixed error rows
- line 5: `https://pgexercises.com/questions/aggregates/` -> `corpus/tutorial/html/pgexercises/questions/aggregates/index.html` (exists, status set to `downloaded`)

## Missing pages (kept as error)
- line 9: `https://pgexercises.com/about.html` -> missing `corpus/tutorial/html/pgexercises/about.html`
- line 32: `https://pgexercises.com/questions/joins/threejoin.html` -> missing `corpus/tutorial/html/pgexercises/questions/joins/threejoin.html`
- line 36: `https://pgexercises.com/questions/date/extract.html` -> missing `corpus/tutorial/html/pgexercises/questions/date/extract.html`
- line 39: `https://pgexercises.com/questions/date/interval2.html` -> missing `corpus/tutorial/html/pgexercises/questions/date/interval2.html`
- line 43: `https://pgexercises.com/questions/string/substr.html` -> missing `corpus/tutorial/html/pgexercises/questions/string/substr.html`
- line 47: `https://pgexercises.com/questions/string/concat.html` -> missing `corpus/tutorial/html/pgexercises/questions/string/concat.html`
- line 50: `https://pgexercises.com/questions/recursive/getupward.html` -> missing `corpus/tutorial/html/pgexercises/questions/recursive/getupward.html`
- line 53: `https://pgexercises.com/questions/updates/updatecalculated.html` -> missing `corpus/tutorial/html/pgexercises/questions/updates/updatecalculated.html`
- line 56: `https://pgexercises.com/questions/updates/update.html` -> missing `corpus/tutorial/html/pgexercises/questions/updates/update.html`
- line 60: `https://pgexercises.com/questions/updates/delete.html` -> missing `corpus/tutorial/html/pgexercises/questions/updates/delete.html`

## Coverage note
- Missing PGExercises pages are partially covered by curated practice materials (`curated/*/sql_practice_tasks.ru.md`) and broader SQL tutorial topics.
- Embeddings can be recalculated without these pages; report this limitation in final audit.
