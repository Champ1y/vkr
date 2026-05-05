---
title: "Using EXPLAIN - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Using_EXPLAIN.html"
source_url: "https://wiki.postgresql.org/wiki/Using_EXPLAIN"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Using EXPLAIN - PostgreSQL wiki

Using EXPLAIN - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Using EXPLAIN
Jump to navigation
Jump to search
Figuring out why a statement is taking so long to execute is done with the
EXPLAIN
command.  You can run EXPLAIN multiple ways; if you use EXPLAIN ANALYZE, it will actually run the statement and let you compare what the planner thought was going to happen with what actually did.  Note that if the statement changes data, that will also happen when you run with EXPLAIN ANALYZE; if you just use EXPLAIN the statement doesn't do anything to the database.
There are some tools available to help interpret EXPLAIN output:
pgadmin includes a visual EXPLAIN tool that helps map out what's actually happening.  See
Reading PgAdmin Graphical Explain Plans
.
Visual Explain, originally a
RedHat component
that has been kept current and improved by EnterpriseDB, comes bundled with the EnterpriseDB Advanced Server package.  It can be built to run against other PostgreSQL installations using the source code to their
Developer Studio
package.
PostgreSQL execution plan visualizer
displays a visual tree of the query plan with several details per node (
GitHub repository
). An
older version
exists, but does not render plans with parallel workers correctly (
blog post
,
GitHub repository
).
explain.depesz.com
shows explain plan with extracted summarized times, and highlights based on chosen criteria.
pgMustard
is a commercial tool (with a free trial) which visualizes EXPLAIN output, and gives tips to improve performance.
explain-postgresql.com
analyzes EXPLAIN plan from PostgreSQL and related (Greenplum, Citus, TimescaleDB and Amazon RedShift). Shows plan and node details and visualizations with piechart, flowchart and tilemap, also gives smart recommendations to improve query. Free for personal use.
And there are a few tutorials on this subject, many of which are titled "Explaining Explain". While many deal with direct fundamentals, they are listed here chronologically:
Efficient SQL
by Greg Sabino Mullane (2003)
Explaining Explain:
pdf
by Robert Treat (2005)
Explaining Explain
by Lukas Smith (2006)
Explaining Explain
by Greg Stark (2008)
Query Execution Techniques in PostgreSQL
by Neil Conway
Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT
by Jim Nasby
The PostgreSQL Query Planner
by Robert Haas (2010)
PostgreSQL 9.0 High Performance
(2010) is a book with a long discussion of how to use EXPLAIN, read the resulting query plans, and make changes to get different plans.
Understanding Explain
by Guillaume Lelarge (2012) is a 42 page guide
EXPLAIN Explained
is a talk by Josh Berkus (2016)
Explaining the query optimizer
by Bruce Momjian (
2016 video
-- skip to 1:24:00 or so)
Reading Postgres query plans for beginners
by David Conlin (2018)
Postgres EXPLAIN Explained
by Baron Schwartz (2019)
EXPLAIN glossary
by Michael Christofides (2020)
PostgreSQL EXPLAIN
by Devart (2023)
There is also a section in the online documentation that discusses performance tips:
Performance Tips
A common problem that causes the planner to make bad decisions is not keeping
Planner Statistics
updated.  Another is leaving the tuning parameters that let the server know how memory is available at the very small defaults.  For example, in the stock configuration, sorts that take more than 4MB are swapped to disk as being too big to process in memory.
Tuning Your PostgreSQL Server
covers good practices for sizing the memory and other tuning parameters that most impact query planning.
One thing you do when stumped by a plan is to submit the full EXPLAIN ANALYZE output, along with the schema of the involved queries, to the
pgsql-performance
mailing list. To get a useful reply more quickly, please read
SlowQueryQuestions
before posting. Note that if you're not running a relatively current version of PostgreSQL, it's quite possible the answer you'll get is that the problem is resolved in a later one.  It may save you some time to try at least the most current update to the version you're using (i.e. upgrade to 11.6 if that's the current latest rev and you're using 11.3) and see if that improves the plan you get.
An advanced technique here is to save your explain plans over time and see how they change as the amount of data in the table grows.  This can give you an idea if you're collecting statistics aggressively enough.  A simple pl/pgsql example is at
generic options for explain
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
