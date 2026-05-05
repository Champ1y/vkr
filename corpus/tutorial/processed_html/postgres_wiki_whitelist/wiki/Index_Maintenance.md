---
title: "Index Maintenance - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Index_Maintenance.html"
source_url: "https://wiki.postgresql.org/wiki/Index_Maintenance"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Index Maintenance - PostgreSQL wiki

Index Maintenance - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Index Maintenance
Jump to navigation
Jump to search
One day, you will probably need to cope with
routine reindexing
on your database, particularly if you don't use VACUUM aggressively enough.  A particularly handy command in this area is
CLUSTER
, which can help with other types of cleanup.
Avoid using
VACUUM FULL
in versions 8.4 and earlier.
Index summary
Here's a sample query to pull the number of rows, indexes, and some info about those indexes for each table.
Performance Snippets
Index summary
Works with PostgreSQL
>=9.4
Written in
SQL
Depends on
Nothing
SELECT
pg_class
.
relname
,
pg_size_pretty
(
pg_class
.
reltuples
::
bigint
)
AS
rows_in_bytes
,
pg_class
.
reltuples
AS
num_rows
,
COUNT
(
*
)
AS
total_indexes
,
COUNT
(
*
)
FILTER
(
WHERE
indisunique
)
AS
unique_indexes
,
COUNT
(
*
)
FILTER
(
WHERE
indnatts
=
1
)
AS
single_column_indexes
,
COUNT
(
*
)
FILTER
(
WHERE
indnatts
IS
DISTINCT
FROM
1
)
AS
multi_column_indexes
FROM
pg_namespace
LEFT
JOIN
pg_class
ON
pg_namespace
.
oid
=
pg_class
.
relnamespace
LEFT
JOIN
pg_index
ON
pg_class
.
oid
=
pg_index
.
indrelid
WHERE
pg_namespace
.
nspname
=
'public'
AND
pg_class
.
relkind
=
'r'
GROUP
BY
pg_class
.
relname
,
pg_class
.
reltuples
ORDER
BY
pg_class
.
reltuples
DESC
;
Index size/usage statistics
Table & index sizes along which indexes are being scanned and how many tuples are fetched.  See
Disk Usage
for another view that includes both table and index sizes.
Performance Snippets
Index statistics
Works with PostgreSQL
>=8.1
Written in
SQL
Depends on
Nothing
SELECT
t
.
schemaname
,
t
.
tablename
,
c
.
reltuples
::
bigint
AS
num_rows
,
pg_size_pretty
(
pg_relation_size
(
c
.
oid
))
AS
table_size
,
psai
.
indexrelname
AS
index_name
,
pg_size_pretty
(
pg_relation_size
(
i
.
indexrelid
))
AS
index_size
,
CASE
WHEN
i
.
indisunique
THEN
'Y'
ELSE
'N'
END
AS
"unique"
,
psai
.
idx_scan
AS
number_of_scans
,
psai
.
idx_tup_read
AS
tuples_read
,
psai
.
idx_tup_fetch
AS
tuples_fetched
FROM
pg_tables
t
LEFT
JOIN
pg_class
c
ON
t
.
tablename
=
c
.
relname
LEFT
JOIN
pg_index
i
ON
c
.
oid
=
i
.
indrelid
LEFT
JOIN
pg_stat_all_indexes
psai
ON
i
.
indexrelid
=
psai
.
indexrelid
WHERE
t
.
schemaname
NOT
IN
(
'pg_catalog'
,
'information_schema'
)
ORDER
BY
1
,
2
;
Duplicate indexes
Finds multiple indexes that have the same set of columns, same opclass, expression and predicate -- which make them equivalent.
Usually
it's safe to drop one of them, but I give no guarantees. :)
SELECT
pg_size_pretty
(
sum
(
pg_relation_size
(
idx
))::
bigint
)
as
size
,
(
array_agg
(
idx
))[
1
]
as
idx1
,
(
array_agg
(
idx
))[
2
]
as
idx2
,
(
array_agg
(
idx
))[
3
]
as
idx3
,
(
array_agg
(
idx
))[
4
]
as
idx4
FROM
(
SELECT
indexrelid
::
regclass
as
idx
,
(
indrelid
::
text
||
E
'\n'
||
indclass
::
text
||
E
'\n'
||
indkey
::
text
||
E
'\n'
||
coalesce
(
indexprs
::
text
,
''
)
||
E
'\n'
||
coalesce
(
indpred
::
text
,
''
))
as
key
FROM
pg_index
)
sub
GROUP
BY
key
HAVING
count
(
*
)
>
1
ORDER
BY
sum
(
pg_relation_size
(
idx
))
DESC
;
Index Bloat
Based on check_postgres
One of the common needs for a REINDEX is when indexes become bloated due to either sparse deletions or use of VACUUM FULL (with pre 9.0 versions).  An estimator for the amount of bloat in a table has been included in the
check_postgres
script, which you can call directly or incorporate into a larger monitoring system.  Scripts based on this code and/or its concepts from other sources include:
bloat view
(Dimitri Fontaine) - extracted from check_postgres
Visualizing Postgres
- index_byte_sizes view (Michael Glaesemann, myYearbook)
OmniTI Tasty Treats for PostgreSQL
- shell and Perl pg_bloat_report scripts
New query
A new query has been created to have a better bloat estimate for Btree indexes. Unlike the query from check_postgres, this one focus only on BTree index its disk layout.
See
articles
about it.
The monitoring script
check_pgactivity
is including a check based on this work.
Summarize keyspace of a B-Tree index
Performance Snippets
Show database bloat
Works with PostgreSQL
>=9.3
Written in
SQL
Depends on
contrib/pageinspect
The following query uses contrib/pageinspect to summarize the keyspace of a B-Tree quickly. This can be useful to experts that wish to determine exactly how an index may have become unbalanced over time. It visualizes the keyspace of the index.
The query outputs the highkey for every page, starting from the root and working down, in logical/keyspace order.
If the query takes too long to execute, consider uncommenting "/* and level > 0 */" to make it only include internal pages.
See also:
"PostgreSQL index bloat under a microscope" blogpost
Note:
You are expected to change "pgbench_accounts_pkey" to the name of the index that is to be summarized.
WITH
RECURSIVE
index_details
AS
(
SELECT
'pgbench_accounts_pkey'
::
text
idx
),
size_in_pages_index
AS
(
SELECT
(
pg_relation_size
(
idx
::
regclass
)
/
(
2
^
13
))::
int4
size_pages
FROM
index_details
),
page_stats
AS
(
SELECT
index_details
.
*
,
stats
.
*
FROM
index_details
,
size_in_pages_index
,
lateral
(
SELECT
i
FROM
generate_series
(
1
,
size_pages
-
1
)
i
)
series
,
lateral
(
SELECT
*
FROM
bt_page_stats
(
idx
,
i
))
stats
),
meta_stats
AS
(
SELECT
*
FROM
index_details
s
,
lateral
(
SELECT
*
FROM
bt_metap
(
s
.
idx
))
meta
),
pages_raw
AS
(
SELECT
*
FROM
page_stats
ORDER
BY
btpo
DESC
),
/* XXX: Note ordering dependency within this CTE */
pages_walk
(
item
,
blk
,
level
)
AS
(
SELECT
1
,
blkno
,
btpo
FROM
pages_raw
WHERE
btpo_prev
=
0
AND
btpo
=
(
SELECT
level
FROM
meta_stats
)
UNION
SELECT
CASE
WHEN
level
=
btpo
THEN
w
.
item
+
1
ELSE
1
END
,
blkno
,
btpo
FROM
pages_raw
i
,
pages_walk
w
WHERE
i
.
btpo_prev
=
w
.
blk
OR
(
btpo_prev
=
0
AND
btpo
=
w
.
level
-
1
)
)
SELECT
/* Uncomment if these details interesting */
/*
idx,
btpo_prev,
btpo_next,
*/
/*
* "level" is level of tree -- 0 is leaf.  First tuple returned is root.
*/
btpo
AS
level
,
/*
* Ordinal number of item on this level
*/
item
AS
l_item
,
/*
* Block number, and details of page
*/
blkno
,
btpo_flags
,
TYPE
,
live_items
,
dead_items
,
avg_item_size
,
page_size
,
free_size
,
/*
* distinct_real_item_keys is how many distinct "data" fields on page
* (excludes highkey).
*
* If this is less than distinct_block_pointers on an internal page, that
* means that there are so many duplicates in its children that there are
* duplicate high keys in children, so the index is probably pretty bloated.
*
* Even unique indexes can have duplicates.  It's sometimes interesting to
* watch out for how many distinct real items there are within leaf pages,
* compared to the number of live items, or total number of items.  Ideally,
* these will all be exactly the same for unique indexes.
*/
distinct_real_item_keys
,
/*
* Per pageinspect docs, first item on non-rightmost page on level is "high
* key" item, which represents an upper bound on items on the page.
* (Rightmost pages are sometimes considered to have a conceptual "positive
* infinity" item, and are shown to have a high key that's NULL by this query)
*
* This can be used to visualize how finely or coarsely separated the
* keyspace is.
*
* Note that below int4_from_page_data() function could produce more useful
* visualization of split points.
*/
CASE
WHEN
btpo_next
!=
0
THEN
first_item
END
AS
highkey
,
/*
* distinct_block_pointers is table blocks that are pointed to by items on
* the page (not including high key, which doesn't point anywhere).
*
* This is interesting on leaf pages, because it indicates how fragmented the
* index is with respect to table accesses, which is important for range
* queries.
*
* This should be redundant on internal levels, because all downlinks in internal
* pages point to distinct blocks in level below.
*/
distinct_block_pointers
FROM
pages_walk
w
,
pages_raw
i
,
lateral
(
SELECT
count
(
distinct
(
case
when
btpo_next
=
0
or
itemoffset
>
1
then
(
data
collate
"C"
)
end
))
as
distinct_real_item_keys
,
count
(
distinct
(
case
when
btpo_next
=
0
or
itemoffset
>
1
then
(
ctid
::
text
::
point
)[
0
]::
bigint
end
))
as
distinct_block_pointers
,
(
array_agg
(
data
))[
1
]
as
first_item
FROM
bt_page_items
(
idx
,
blkno
)
)
items
where
w
.
blk
=
i
.
blkno
/* Uncomment to avoid showing leaf level (faster): */
/* and level > 0*/
ORDER
BY
btpo
DESC
,
item
;
Interpreting bt_page_items() "data" field as a little-endian int4 attribute
Performance Snippets
Show database bloat
Works with PostgreSQL
>=9.2
Written in
SQL
Depends on
contrib/pageinspect
The following convenience functions can be used to display the "data" field in bt_page_items() as their native type, at least for indexes whose pg_attribute entries consist of a single int4/integer attribute. This includes SERIAL primary key indexes. It can be used to make the above "Summarize keyspace of a B-Tree index" query display the keyspace split points using native type representation.
Note:
The byteswap is only necessary on little-endian (Intel) CPUs.
--
-- Sources:
--
-- https://stackoverflow.com/questions/17208945/whats-the-easiest-way-to-represent-a-bytea-as-a-single-integer-in-postgresql
-- https://stackoverflow.com/questions/11142235/convert-bigint-to-bytea-but-swap-the-byte-order
--
create
or
replace
function
reverse_bytes_iter
(
bytes
bytea
,
length
int
,
midpoint
int
,
index
int
)
returns
bytea
as
$$
select
case
when
index
>=
midpoint
then
bytes
else
reverse_bytes_iter
(
set_byte
(
set_byte
(
bytes
,
index
,
get_byte
(
bytes
,
length
-
index
)),
length
-
index
,
get_byte
(
bytes
,
index
)
),
length
,
midpoint
,
index
+
1
)
end
;
$$
language
sql
immutable
strict
;
create
or
replace
function
reverse_bytes
(
bytes
bytea
)
returns
bytea
as
$$
select
reverse_bytes_iter
(
bytes
,
octet_length
(
bytes
)
-
1
,
octet_length
(
bytes
)
/
2
,
0
)
$$
language
sql
immutable
strict
;
create
or
replace
function
int4_from_bytea
(
bytea
)
returns
int4
as
$$
select
(
'x'
||
right
(
$
1
::
text
,
6
))::
bit
(
24
)::
int
;
$$
language
sql
immutable
strict
;
create
or
replace
function
int4_from_page_data
(
text
)
returns
int4
as
$$
select
int4_from_bytea
(
reverse_bytes
(
decode
(
$
1
,
'hex'
)));
$$
language
sql
immutable
strict
;
--
-- Use:
--
--  postgres=# select *, int4_from_page_data(data) from bt_page_items('f', 1) limit 15;
--   itemoffset │    ctid    │ itemlen │ nulls │ vars │          data           │ int4_from_page_data
--  ────────────┼────────────┼─────────┼───────┼──────┼─────────────────────────┼─────────────────────
--            1 │ (17698,69) │      16 │ f     │ f    │ 5c 00 00 00 00 00 00 00 │                  92
--            2 │ (0,1)      │      16 │ f     │ f    │ 01 00 00 00 00 00 00 00 │                   1
--            3 │ (8849,126) │      16 │ f     │ f    │ 01 00 00 00 00 00 00 00 │                   1
--            4 │ (17699,25) │      16 │ f     │ f    │ 01 00 00 00 00 00 00 00 │                   1
--            5 │ (17699,26) │      16 │ f     │ f    │ 01 00 00 00 00 00 00 00 │                   1
--            6 │ (0,2)      │      16 │ f     │ f    │ 02 00 00 00 00 00 00 00 │                   2
--            7 │ (8849,125) │      16 │ f     │ f    │ 02 00 00 00 00 00 00 00 │                   2
--            8 │ (17699,23) │      16 │ f     │ f    │ 02 00 00 00 00 00 00 00 │                   2
--            9 │ (17699,24) │      16 │ f     │ f    │ 02 00 00 00 00 00 00 00 │                   2
--           10 │ (0,3)      │      16 │ f     │ f    │ 03 00 00 00 00 00 00 00 │                   3
--           11 │ (8849,124) │      16 │ f     │ f    │ 03 00 00 00 00 00 00 00 │                   3
--           12 │ (17699,21) │      16 │ f     │ f    │ 03 00 00 00 00 00 00 00 │                   3
--           13 │ (17699,22) │      16 │ f     │ f    │ 03 00 00 00 00 00 00 00 │                   3
--           14 │ (0,4)      │      16 │ f     │ f    │ 04 00 00 00 00 00 00 00 │                   4
--           15 │ (8849,123) │      16 │ f     │ f    │ 04 00 00 00 00 00 00 00 │                   4
--  (15 rows)
Unused Indexes
Since indexes add significant overhead to any table change operation, they should be removed if they are not being used for either queries or constraint enforcement (such as making sure a value is unique).  How to find such indexes:
Index pruning techniques
Finding unused indexes
Finding useless indexes
'Monitor unused indexes' by Johnny Morano
References
Index statistics queries from
"Refactoring SQL Applications" review
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
