---
title: "Planner Statistics - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Planner_Statistics.html"
source_url: "https://wiki.postgresql.org/wiki/Planner_Statistics"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Planner Statistics - PostgreSQL wiki

Planner Statistics - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Planner Statistics
Jump to navigation
Jump to search
In order for queries to execute quickly, the PostgreSQL query planner needs to have accurate statistics about the tables in your database.  See
Statistics Used by the Planner
and
Using EXPLAIN
for more information about this.
Statistics are updated by running the
VACUUM ANALYZE
, either against the whole database or against the table you're interested in.  Starting in PostgreSQL 8.1, you can automate this task by using the
Auto-Vacuum Daemon
.  This can take some configuration to setup usefully, in PostgreSQL 8.3 auto-vacuum is intelligent and well tuned enough that it's turned on by default.
The most popular tunable that controls statistics gathering is
default_statistics_target
, which can be set per table and column with
ALTER TABLE SET STATISTICS
.  The useful range is generally 10 (the default) to 100.  Higher settings can cause the statistics collection process itself to be a drag on performance.  For more information, see the long thread on
Better default_statistics_target
-
Part 2
.
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
