---
title: "Logging Difficult Queries - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Logging_Difficult_Queries.html"
source_url: "https://wiki.postgresql.org/wiki/Logging_Difficult_Queries"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Logging Difficult Queries - PostgreSQL wiki

Logging Difficult Queries - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Logging Difficult Queries
Jump to navigation
Jump to search
If you want to find the queries that are taking the longest on your system, you can do that by setting
log_min_duration_statement
to a positive value representing how many milliseconds the query has to run before it's logged.  In PostgreSQL 8.4+, you can use
pg_stat_statements
for this purpose as well, without needing an external utility.
Some utilities that can help sort through this data are:
pgFouine
.  Its documentation has some more tips on log_min_duration_statement and related logging parameters
pgBadger
.  Its documentation also includes advice on log_min_duration_statement and related logging parameters
PQA
EPQA
pgsi
- see
introduction
If you are using these tools, you might even consider a period where set the minimum duration to 0 and therefore get all statements logged.  This is will be intensive on the logging side, but running that data through one of the tools will give you a lot of insight into what your server is doing.
One thing that can cause queries to pause for several seconds is a checkpoint.  If you periodically see many queries all taking several seconds all finishing around the same time, consider
Logging Checkpoints
and seeing if those times line up, and if so tune appropriately.
auto-explain
In PostgreSQL, the
Auto-Explain
contrib module allows saving explain plans only for queries that exceed some time threshold.  Seeing the bad plans can help determine why queries are slow, instead of just that they are slow.  See
Waiting for 8.4 - auto-explain
for an example.
Navigation menu
Page actions
Page
Discussion
Read
View source
History
Page actions
Page
Discussion
More
Tools
Personal tools
Log in
