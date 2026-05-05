---
title: "VACUUM FULL - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/VACUUM_FULL.html"
source_url: "https://wiki.postgresql.org/wiki/VACUUM_FULL"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# VACUUM FULL - PostgreSQL wiki

VACUUM FULL - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
VACUUM FULL
Jump to navigation
Jump to search
This page contains
historical information or deprecated articles
.
This document is obsolete for PostgreSQL 9.0 and above. Most of the content applies only to PostgreSQL 8.4 and below.
VACUUM vs VACUUM FULL (PostgreSQL 8.4 and older)
This document is obsolete for PostgreSQL 9.0 and above. Much of the content applies only to PostgreSQL 8.4 and below.
The
VACUUM
command and associated autovacuum process are PostgreSQL's way of controlling MVCC bloat. The
VACUUM
command has two main forms of interest - ordinary
VACUUM
, and
VACUUM FULL
. These two commands are actually quite different and should not be confused.
VACUUM
scans a table, marking tuples that are no longer needed as free space so that they can be overwritten by newly inserted or updated data. See
Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT
and the PostgreSQL documentation on
MVCC
for a detailed explanation of this. Note that you should rarely need to use the
VACUUM
command directly on a modern PostgreSQL database, as
autovacuum
should take care of it for you if properly set up.
VACUUM FULL
, unlike
VACUUM
, touches data that has not been deleted. On pre-9.0 versions of PostgreSQL, it moves data into spaces earlier in the file that have been freed. Once it has created a free space at the end of the file, it truncates the file so that the OS knows that space is free and may be reused for other things. Moving in-use data around this way can have adverse side-effects, including taking heavy weight locks, increased i/o, and adding index bloat. On older systems, there are better ways to free space if you need to, and better ways to optimize tables (see below) so you should essentially never use
VACUUM FULL
on a pre-9.x system. Even on 9.x and above, the system is designed with the goal that you should never be running
VACUUM FULL
regularly, and doing so can have costs like huge WAL archive output and high loads on any streaming replication servers.
For clarity,
9.0 changes VACUUM FULL
.  As covered in the
documentation
, the VACUUM FULL implementation has been changed to one that's similar to using CLUSTER in older versions.  This gives a slightly different set of trade-offs from the older VACUUM FULL described here.  While the potential to make the database slower via index bloating had been removed by this change, it's still something you may want to avoid doing, due to the locking and general performance overhead of a VACUUM FULL.
When to use
VACUUM FULL
and when not to
Many people, either based on misguided advice on the 'net or on the assumption that it must be "better", periodically run
VACUUM FULL
on their tables. This is generally not recommended and in some cases can make your database slower, not faster.
VACUUM FULL
is only needed when you have a table that is mostly dead rows - ie, the vast majority of its contents have been deleted. It should not be used for table optimization or periodic maintenance, as it's generally counterproductive. In most cases the freed space will be promptly re-allocated, possibly increasing file-system-level fragmentation and requiring file system space allocations that're slower than just re-using existing free space within a table.
When you run
VACUUM FULL
on a table, that table is locked for the duration of the operation, so nothing else can work with the table.
VACUUM FULL
is
much
slower than a normal
VACUUM
, so the table may be unavailable for a while.
More importantly, on pre-9.0 systems, while
VACUUM FULL
compacts the table, it does not compact the indexes - and in fact may increase their size, thus slowing them down, causing more disk I/O when the indexes are used, and increasing the amount of memory they require. A
REINDEX
may be required after
VACUUM FULL
on PostgreSQL versions older than 9.0. See the main documentation's
notes on VACUUM vs VACUUM FULL
.
What to use instead
If you shouldn't use regularly use
VACUUM FULL
(or use it at all on versions older than 9.0) ... what should you be using?
Autovacuum
If
autovacuum
is running frequently enough and aggressively enough, your tables should never grow ("bloat") due to unreclaimed dead rows, so you should never need to return "dead" space to the OS.
Autovacuum continues to improve dramatically with every PostgreSQL version, and is a very good reason to make sure you are running the latest version. For example, with 8.4 the free space map is now managed automatically, removing a no-longer-necessary tuning parameter and eliminating a major source of table bloat.
If autovacuum isn't doing enough to keep your tables and indexes bloat-free, tune it, don't supplement it with manual vacuuming and reindexing. You may need to increase your free space map settings (pre-8.4), tune autovacuum to run more frequently, and/or tell autovacuum to vacuum certain frequently-updated tables more aggressively than others.
VACUUM
Unless you need to return space to the OS so that other tables or other parts of the system can use that space, or you are trying to repair a table that has bloated out of control due to insufficient autovacuum, you should use
VACUUM
instead of
VACUUM FULL
.
If you need to manually
VACUUM
your tables at any time other than when running major admin or update tasks that rewrite large parts of your tables, you probably don't have autovacuum set up well enough.
CLUSTER
If you're trying to "optimise" your tables by packing them down and removing table bloat that's accumulated due to (say) insufficiently aggressive autovacuuming, or you're trying to return dead space in a table to the operating system, it's fine to use VACUUM FULL in PostgreSQL 9.0 and above.
Consider setting a FILLFACTOR of less than the default 100, so the rewritten table has some free space pre-alloacated within it for updates and new inserts; otherwise you'll just get file system allocations as soon as you do anything to the table.
In older versions, it's preferable to use
CLUSTER
. It runs a
lot
faster than pre-9.0
VACUUM FULL
and will compact and optimise the indexes as well as the table its self. However, you will need enough free space to hold all the in-use data from the table while
CLUSTER
runs. As with post-9.0 VACUUM FULL, a non-default FILLFACTOR may be wise.
TRUNCATE TABLE
If you've been using
VACUUM FULL
to free space from a table that's periodically completely emptied using
DELETE FROM tablename;
(without a
WHERE
clause), you can use
TRUNCATE TABLE
to replace those two steps with one much,
much
faster one.
Instead of:
DELETE FROM tablename;
VACUUM FULL tablename;
write:
TRUNCATE TABLE tablename;
Please make sure to read the caveats in the notes on the
TRUNCATE TABLE
documentation. If
TRUNCATE TABLE
isn't suitable for your needs, you can use
DELETE
followed by
CLUSTER
instead.
If using
DELETE
on a table that is the target of foreign key references, consider adding an index to the referencing columns. That will allow checks for foreign key enforcement to avoid a sequential scan on the referencing table, making
DELETE
from the referenced table vastly faster.
ALTER TABLE .. SET DATA TYPE
(relevant for 8.4 and below only)
This section is obsolete for PostgreSQL 9.0 and above. Skip it unless you use a very old version.
The problem with
CLUSTER
is that it reorders the table following an index. If the table is not already approximately in that index' order, this will take a long time because it will have to do a scattered read of the table pages over and over as it looks for each tuple. A faster alternative is to request a full table rewrite without requiring a particular order. PostgreSQL versions prior to 9.0 do not offer any direct way to invoke this operation; however, you can use the following workaround. Choose any table column, and use
ALTER TABLE
to change its type
to the same type
. This is obviously going to cause no logical change to the table, but the server will have to rewrite the table, getting rid of dead tuples while at it.
For example, assuming the
an_integer_column
is of type
INTEGER
:
ALTER TABLE your_table ALTER an_integer_column SET DATA TYPE integer;
This trick will not work in PostgreSQL versions 9.1 or later, as it detects that the change in data type is degenerate and so no rewrite is necessary.
SELECT ... INTO
(relevant for 8.4 and below only)
This section is obsolete for PostgreSQL 9.0 and above. Skip it unless you use a very old version.
Sometimes it can be faster to use a
SELECT ... INTO
command to copy data from a bloated table into a new table, then re-create the indexes and finally rename the tables to replace the old one with the new one. It's rarely worth doing this instead of using
CLUSTER
, though, as
CLUSTER
does almost the same thing automatically and can rebuild indexes in parallel. The main reason you may want to use
SELECT ... INTO
instead of
CLUSTER
is if you don't want to sort the table.
Recovering from index bloat caused by
VACUUM FULL
(relevant for 8.4 and below only)
This section is obsolete for PostgreSQL 9.0 and above. Skip it unless you use a very old version.
If you have indexes badly bloated by regular use of
VACUUM FULL
, your best bet is usually going to be to use
CLUSTER
to rewrite the table and rebuild the indexes.
If you can't afford to have the table locked for that long, you can rebuild each index individually while queries continue to run on the table. PostgreSQL unfortunately doesn't have a
REINDEX CONCURRENTLY
command, but it can be simulated with appropriate use of
CREATE INDEX ... CONCURRENTLY
,
ALTER INDEX ... RENAME
and
DROP INDEX
to create new indexes, swap the old and new ones by renaming, and drop the old indexes.  Note that since you can't drop some indexes, such as primary keys, this may not be a possible cleanup technique for all of them.
Originally by --
Ringerc
03:48, 26 November 2009 (UTC)
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
