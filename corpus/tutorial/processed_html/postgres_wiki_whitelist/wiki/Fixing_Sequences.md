---
title: "Fixing Sequences - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Fixing_Sequences.html"
source_url: "https://wiki.postgresql.org/wiki/Fixing_Sequences"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# Fixing Sequences - PostgreSQL wiki

Fixing Sequences - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Fixing Sequences
Jump to navigation
Jump to search
Updating sequence values from table
Administrative Snippets
Fixing Sequences
Works with PostgreSQL
8.4+
Written in
SQL
Depends on
Nothing
A common problem when copying or recreating a database is that database sequences are not updated just by inserting records in the table that sequence is used in.  If you want to make your sequences all start just after whatever values are already there, it's possible to do that for most common configurations like this:
SELECT
'SELECT SETVAL('
||
quote_literal
(
quote_ident
(
sequence_namespace
.
nspname
)
||
'.'
||
quote_ident
(
class_sequence
.
relname
))
||
', COALESCE(MAX('
||
quote_ident
(
pg_attribute
.
attname
)
||
'), 1) ) FROM '
||
quote_ident
(
table_namespace
.
nspname
)
||
'.'
||
quote_ident
(
class_table
.
relname
)
||
';'
FROM
pg_depend
INNER
JOIN
pg_class
AS
class_sequence
ON
class_sequence
.
oid
=
pg_depend
.
objid
AND
class_sequence
.
relkind
=
'S'
INNER
JOIN
pg_class
AS
class_table
ON
class_table
.
oid
=
pg_depend
.
refobjid
INNER
JOIN
pg_attribute
ON
pg_attribute
.
attrelid
=
class_table
.
oid
AND
pg_depend
.
refobjsubid
=
pg_attribute
.
attnum
INNER
JOIN
pg_namespace
as
table_namespace
ON
table_namespace
.
oid
=
class_table
.
relnamespace
INNER
JOIN
pg_namespace
AS
sequence_namespace
ON
sequence_namespace
.
oid
=
class_sequence
.
relnamespace
ORDER
BY
sequence_namespace
.
nspname
,
class_sequence
.
relname
;
Usage would typically work like this:
Save this to a file, say 'reset.sql'
Run the file and save its output in a way that doesn't include the usual headers, then run that output.  Example:
psql -Atq -f reset.sql -o temp
psql -f temp
rm temp
There are a few limitations to this snippet of code you need to be aware of:
It only works on sequences that are owned by a table. If your sequences are not owned, run the following script first:
Fixing sequence ownership
This script changes sequences with OWNED BY to the table and column they're referenced from. NB! Sequences that are referenced by multiple tables or columns are ignored.
(Parts of query shamelessly stolen from OmniTI's
Tasty Treats repository
by Robert Treat)
select
'ALTER SEQUENCE '
||
quote_ident
(
min
(
schema_name
))
||
'.'
||
quote_ident
(
min
(
seq_name
))
||
' OWNED BY '
||
quote_ident
(
min
(
table_name
))
||
'.'
||
quote_ident
(
min
(
column_name
))
||
';'
from
(
select
n
.
nspname
as
schema_name
,
c
.
relname
as
table_name
,
a
.
attname
as
column_name
,
substring
(
d
.
adsrc
from
E
'^nextval\\(''([^'']*)''(?:::text|::regclass)?\\)'
)
as
seq_name
from
pg_class
c
join
pg_attribute
a
on
(
c
.
oid
=
a
.
attrelid
)
join
pg_attrdef
d
on
(
a
.
attrelid
=
d
.
adrelid
and
a
.
attnum
=
d
.
adnum
)
join
pg_namespace
n
on
(
c
.
relnamespace
=
n
.
oid
)
where
has_schema_privilege
(
n
.
oid
,
'USAGE'
)
and
n
.
nspname
not
like
'pg!_%'
escape
'!'
and
has_table_privilege
(
c
.
oid
,
'SELECT'
)
and
(
not
a
.
attisdropped
)
and
d
.
adsrc
~
'^nextval'
)
seq
group
by
seq_name
having
count
(
*
)
=
1
;
This snippet finds orphaned sequences that aren't owned by any column. It can be helpful to run this, to double-check that the above query did its job right.
select
ns
.
nspname
as
schema_name
,
seq
.
relname
as
seq_name
from
pg_class
as
seq
join
pg_namespace
ns
on
(
seq
.
relnamespace
=
ns
.
oid
)
where
seq
.
relkind
=
'S'
and
not
exists
(
select
*
from
pg_depend
where
objid
=
seq
.
oid
and
deptype
=
'a'
and
classid
=
'pg_class'
::
regclass
)
order
by
seq
.
relname
;
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
