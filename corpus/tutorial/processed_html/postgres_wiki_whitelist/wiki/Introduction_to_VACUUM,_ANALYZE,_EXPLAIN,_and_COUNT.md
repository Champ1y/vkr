---
title: "Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Introduction_to_VACUUM,_ANALYZE,_EXPLAIN,_and_COUNT.html"
source_url: "https://wiki.postgresql.org/wiki/Introduction_to_VACUUM,_ANALYZE,_EXPLAIN,_and_COUNT"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT - PostgreSQL wiki

Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Introduction to VACUUM, ANALYZE, EXPLAIN, and COUNT
Jump to navigation
Jump to search
These articles are copyright 2005 by
Jim Nasby
and were written while he was employed by
Pervasive Software
.  They appear here by permission of the author.
Vacuum the Dirt out of Your Database
A key component of any database is that it’s ACID. There's an excellent
article about ACID on Wikipedia
,
but in short ACID is what protects the data in your database. If a
database isn't ACID, there is nothing to ensure that your data is safe
against seemingly random changes. This is why almost all popular
databases are ACID compliant (MySQL in certain modes is a notable
exception).
There are many facets to ACIDity, but MVCC (
Multiversion Concurrency Control
)
is mostly concerned with I, or Isolation. Isolation ensures that
multiple users accessing the same data will get the same results as if
there was only one user accessing the data at a time.
A simple way to ensure this is to not allow any users to modify a
piece of data if any other users are currently reading that data. This
guarantees that the data can’t change until everyone is done reading
it. This is accomplished by using "read locking," and it’s how many
databases operate. But read locking has some serious drawbacks.
Imagine a database that's being used on a Web site. Most pages on
the site will make at least one query against the database, and many
pages will make several. Of course, there are other pages that will be
modifying data as well.
Now remember for each row that is read from the database, a read
lock must be acquired. So every page is going to be acquiring many
locks, sometimes hundreds of them. Every time a lock is acquired or
released, the database isn't processing your data; it's worrying about
these locks.
But what about those pages that update data? You can’t update
anything that's being read, and likewise anything that's being updated
can't be read. When someone wants to update data, they have to wait
until everyone who's currently reading it is done. Meanwhile, to ensure
that the person who wants to update will be able to eventually do so,
new queries that want to read that data will block until after the
update happens. Therefore, by having just one query that wants to do an
update, you have a large amount of people who are waiting for the
update to complete, and the update is waiting on a whole lot of reads
to finish.
Consider the same situation with MVCC. None of the queries that are
reading data need to acquire any locks at all. That's a lot of locks
that the database doesn't need to worry about, so it can spend more
time handling your data (which is what you want the database to do
anyway). More importantly, the update query doesn't need to wait on any
read queries, it can run immediately, and the read queries do not need
to wait on the update query either. Instead of having several queries
waiting around for other queries to finish, your Web site just keeps
humming along.
Of course, MVCC doesn't come without a downside. The ‘MV’ in MVCC
stands for Multi Version. This means that multiple versions of the same
data will be kept any time that data changes. Oracle does this by
rolling old data into an "undo log." PostgreSQL doesn't use an undo
log; instead it keeps multiple versions of data in the base tables.
This means that there is much less overhead when making updates, and
you must occasionally remove the old versions. This is one of the
things VACUUM does.
The way PostgreSQL manages these multiple versions is by storing
some extra information with every row. This information is used to
determine what transactions should be able to see the row. If the row
is an old version, there is information that tells PostgreSQL where to
find the new version of the row.
This information is needed to be able to lock rows during an update.
Consider this scenario: a row is inserted into a table that has a
couple indexes, and that transaction commits. Several updates happen on
that row. Each update will create a new row in all indexes, even if the
index key didn't change. And each update will also leave an old version
of the row in the base table, one that has been updated to point to the
location of the new version of the row that replaces it. All of the old
data will stick around until the
vacuum
is run on that table. In a busy
system, it doesn't take very long for all the old data to translate
into a lot of wasted space. And it's very difficult to reclaim that
space if it grows to an unacceptable level.
What this means to those who want to keep their PostgreSQL database
performing well is that proper vacuuming is critical. This is
especially true on any tables that see a heavy update (or
insert/delete) load, such as a table used to implement some kind of a
queue. Such tables should generally be vacuumed frequently if they are
small--more frequently than
autovacuum
normally would provide. For
more moderate loads, autovacuum will often do a good job of keeping
dead space to a minimum. You can and should tune autovacuum to maintain such busy tables
properly, rather than manually vacuuming them.
Note that
VACUUM FULL
is very expensive compared to a regular VACUUM. It rebuilds the entire table and all indexes from scratch, and it holds a write lock on the table while it's working. That will block all DML.
VACUUM FULL worked differently prior to 9.0. It actually moved tuples around in the table, which was slow and caused table bloat. It's use is discouraged. Some people used CLUSTER instead, but be aware that prior to 9.0 CLUSTER was not MVCC safe and could result in data loss.
Is PostgreSQL remembering what you vacuumed?
When the database needs to add new data to a table as the result of an INSERT or UPDATE, it needs to find someplace to store that data. There are 3 ways it could do this:
Scan through the table to find some free space
Just add the information to the end of the table
Remember what pages in the table have free space available, and use one of them
Option 1 would obviously be extremely slow. Imagine potentially reading the entire table every time you wanted to add or update data! Option 2 is fast, but it would result in the table growing in size every time you added a row. That leaves option 3, which is where the FSM comes in. The FSM is where PostgreSQL keeps track of pages that have free space available for use. Any time it needs space in a table it will look in the FSM first; if it can't find any free space for the table it will fall back to adding the information to the end of the table.
What's all this mean in real life? The only way pages are put into the FSM is via a VACUUM. But the FSM is limited in size, so each table is only allowed a certain amount of room to store information about pages that have free space. If a table has more pages with free space than room in the FSM, the pages with the lowest amount of free space aren't stored at all. This means the space on those pages won't be used until at least the next time that table is vacuumed.
The net result is that in a database with a lot of pages with free space on them (such as a database that went too long without being vacuumed) will have a difficult time reusing free space.
Fortunately, there is an easy way to get an estimate for how much free space is needed: VACUUM VERBOSE. Any time VACUUM VERBOSE is run on an entire database, (ie: vacuumdb -av) the last two lines contain information about FSM utilization:
INFO: free space map: 81 relations, 235349 pages stored; 220672 total pages needed
DETAIL: Allocated FSM size: 1000 relations + 2000000 pages = 11817 kB shared memory.
The first line indicates that there are 81 relations in the FSM and that those 81 relations have stored 235349 pages with free space on them. The database estimates that 220672 slots are needed in the FSM.
The second line shows actual FSM settings. This PostgreSQL installation is set to track 1000 relations (max_fsm_relations) with a total of 2000000 free pages (max_fsm_pages). (
Note that these parameters have been removed as of 8.4, as the free space map is managed automatically by PostgreSQL and doesn't require user tuning.
).
Note that this information won't be accurate if there are a number of databases in the PostgreSQL installation and you only vacuum one of them. It's best to vacuum the entire installation.
Configuring the free space map (Pg 8.3 and older only)
The best way to make sure you have enough FSM pages is to periodically vacuum the entire installation using vacuum -av and look at the last two lines of output. You want to ensure that max_fsm_pages is at least as large as the larger of 'pages stored' or 'total pages needed'.
What's even more critical than max_fsm_pages is max_fsm_relations. If the installation has more relations than max_fsm_relations (and this includes temporary tables), some relations will not have any information stored in the FSM at all. This could even include relations that have a large amount of free space available. So it's important to ensure that max_fsm_relations is always larger than what VACUUM VERBOSE reports and includes some headroom. Again, the best way to ensure this is to monitor the results of periodic runs of vacuum verbose.
Using ANALYZE to optimize PostgreSQL queries
Vacuuming isn't the only periodic maintenance your database needs. You also need to analyze the database so that the query planner has table statistics it can use when deciding how to execute a query. Simply put: Make sure you're running ANALYZE frequently enough, preferably via autovacuum. And increase the default_statistics_target (in postgresql.conf) to 100.
PostgreSQL has a very complex query optimizer. Depending on how you want to count, there are nearly a dozen different building blocks that can go into executing a query, and if the query joins several tables there can be hundreds or even thousands of different ways to process those joins. Add everything together and it's not hard to end up with over a million different possible ways to execute a single query.
So, how does the planner determine the best way to run a query? Each of those different 'building blocks' (which are technically called query nodes) has an associated function that generates a cost. This is what you see when you run EXPLAIN:
decibel=# explain select * from customer;
QUERY PLAN
-------------------------------------------------------------
Seq Scan on customer (cost=0.00..12.50 rows=250 width=287)
(1 row)
Without going into too much detail about how to read EXPLAIN output (an article in itself!), PostgreSQL is estimating that this query will return 250 rows, each one taking 287 bytes on average. The cost of obtaining the first row is 0 (not really, it's just a small enough number that it's rounded to 0), and that getting the entire result set has a cost of 12.50. Technically, the unit for cost is "the cost of reading a single database page from disk," but in reality the unit is pretty arbitrary. It doesn't really relate to anything you can measure. Just think of cost in terms of "units of work"; so running this query will take "12.5 units of work."
How did the database come up with that cost of 12.5? The planner called the cost estimator function for a Seq Scan. That function then looked up a bunch of statistical information about the "customer" table and used it to produce an estimate of how much work it would take to execute the query. Now we get to the heart of the matter: Table Statistics!
PostgreSQL keeps two different sets of statistics about tables. The first set has to do with how large the table is. This information is stored in the pg_class system table. The "relpages" field is the number of database pages that are being used to store the table, and the "reltuples" field is the number of rows in the table. The value of reltuples/relpages is the average number of rows on a page, which is an important number for the planner to know. Typically a query will only be reading a small portion of the table, returning a limited number of rows. Because all IO operations are done at the page level, the more rows there are on a page the fewer pages the database has to read to get all the rows it needs.
The other set of statistics PostgreSQL keeps deal more directly with the question of how many rows a query will return. These statistics are kept on a field-by-field basis. To see this idea in action, let's query for a more limited set of rows:
decibel=# explain select * from customer where state='TX';
QUERY PLAN
----------------------------------------------------------------------------------
Index Scan using customer__state on customer (cost=0.00..5.96 rows=1 width=287)
Index Cond: (state = 'TX'::bpchar)
(2 rows)
Now the planner thinks that we'll only get one row back. It estimates this by looking at pg_stats.histogram_bounds, which is an array of values. Each value defines the start of a new "bucket," where each bucket is approximately the same size. For example if we had a table that contained the numbers 1 through 10 and we had a histogram that was 2 buckets large, pg_stats.histogram_bounds would be {1,5,10}. This tells the planner that there are as many rows in the table where the value was between 1 and 5 as there are rows where the value is between 5 and 10. If the planner uses that information in combination with pg_class.reltuples, it can estimate how many rows will be returned. In this case, if we do SELECT * FROM table WHERE value <= 5 the planner will see that there are as many rows where the value is <= 5 as there are where the value is >= 5, which means that the query will return half of the rows in the table. There are 10 rows in the table pg_class.reltuples says, so simple math tells us we'll be getting 5 rows back. It can then look at the number of rows on each page and decide how many pages it will have to read. Finally, with all that information, it can make an estimate of how many units of work will be required to execute the query. Of course, it's actually more complicated than that under the covers. For example, if we had instead run the query SELECT * FROM table WHERE value <= 3, the planner now would have to estimate how many rows that would be by interpolating on the histogram data.
One issue with this strategy is that if there are a few values that are extremely common, they can throw everything off. For example, consider this histogram: {1,100,101}. There are as many values between 100 and 101 as there are between 1 and 100. But does that mean that we have every number between 1 and 100? Every other? Do we have a single 1 and a bunch of 50's?
Fortunately, PostgreSQL has two additional statistic fields to help eliminate this problem: most_common_vals and most_common_freqs. As you might guess, these fields store information about the most common values found in the table. The field most_common_vals stores the actual values, and most_common_freqs stores how often each value appears, as a fraction of the total number of rows. So if most_common_vals is {1,2} and most_common_freqs is {0.2,0.11}, 20% of the values in the table are 1 and 11% are 2.
Even with most_common_vals, you can still run into problems. The default is to store the 10 most common values, and 10 buckets in the histogram. But if you have a lot of different values and a lot of variation in the distribution of those values, it's easy to "overload" the statistics. Fortunately, it's easy to increase the number of histogram buckets and common values stored. There are two ways to do this. The first is the postgresql.conf parameter default_statistics_target. Because the only downside to more statistics is more space used in the catalog tables, for most installs I recommend bumping this up to at least 100, and if you have a relatively small number of tables I'd even go to 300 or more.
The second method is to use ALTER TABLE, ie: ALTER TABLE table_name ALTER column_name SET STATISTICS 1000. This overrides default_statistics_target for the column column_name on the table table_name. If you have a large number of tables (say, over 100), going with a very large default_statistics_target could result in the statistics table growing to a large enough size that it could become a performance concern. In cases like this, it's best to keep default_statistics_target moderately low (probably in the 50-100 range), and manually increase the statistics target for the large tables in the database. Note that statistics on a field are only used when that field is part of a WHERE clause, so there is no reason to increase the target on fields that are never searched on.
That's enough about histograms and most common values. There's one final statistic that deals with the likelihood of finding a given value in the table, and that's n_distinct. If this number is positive, it's an estimate of how many distinct values are in the table. If it's negative, it's the ratio of distinct values to the total number of rows. The negative form is used when ANALYZE thinks that the number of distinct values will vary with the size of the table. So if every value in the field is unique, n_distinct will be -1.
Correlation is a measure of the similarity of the row ordering in the table to the ordering of the field. If you scan the table sequentially and the value in a field increases at every row, the correlation is 1. If instead, every field is smaller than the previous one, the correlation is -1. Correlation is a key factor in whether an index scan will be chosen, because a correlation near 1 or -1 means that an index scan won't have to jump around the table a lot.
Finally, avg_width is the average width of data in a field and null_frac is the fraction of rows in the table where the field will be null.
As you can see, a lot of work has gone into keeping enough information so that the planner can make good choices on how to execute queries. But all that framework does no good if the statistics aren't kept up-to-date, or even worse, aren't collected at all. Remember when the planner decided that selecting all the customers in Texas would return 1 row? That was before the table was analyzed. Let's see what reality is:
decibel=# analyze customer;
ANALYZE
decibel=# explain select * from customer where state='TX';
QUERY PLAN
--------------------------------------------------------------
Seq Scan on customer (cost=0.00..65.60 rows=2048 width=107)
Filter: (state = 'TX'::bpchar)
(2 rows)
Not only was the estimate on the number of rows way off, it was off far enough to change the execution plan for the query. This is an example of why it's so important to keep statistics up-to-date. As I mentioned at the start of this article, the best way to do this is to use autovacuum, either the built-in autovacuum in 8.1.x, or contrib/pg_autovacuum in 7.4.x or 8.0.x.
This is obviously a very complex topic. More information about statistics can be found at
http://www.postgresql.org/docs/current/static/planner-stats-details.html
.
PostgreSQL EXPLAIN
Now you know about the importance of giving the query planner up-to-date statistics so that it could plan the best way to execute a query. But how do you know how PostgreSQL is actually executing your query? This is where EXPLAIN comes in.
Let's take a look at a simple example and go through what the various parts mean:
EXPLAIN SELECT * FROM CUSTOMER;
QUERY PLAN
--------------------------------------------------------------
Seq Scan on customer  (cost=0.00..60.48 rows=2048 width=107)
(1 row)
This tells us that the optimizer decided to use a sequential scan to execute the query. It estimates that it will cost 0.00 to return the first row, and that it will cost 60.48 to return all the rows. It thinks there will be 2048 rows returned, and that the average width of each row will be 107 bytes.
But EXPLAIN doesn't actually run the query. If you want to see how close the estimate comes to reality, you need to use EXPLAIN ANALYZE:
EXPLAIN ANALYZE SELECT * FROM CUSTOMER;
QUERY PLAN
------------------------------------------------------------------------------------------------------------
Seq Scan on customer  (cost=0.00..60.48 rows=2048 width=107) (actual time=0.033..6.577 rows=2048 loops=1)
Total runtime: 7.924 ms
(2 rows)
Note that we now have a second set of information; the actual time required to run the sequential scan step, the number of rows returned by that step, and the number of times those rows were looped through (more on that later). We also have a total runtime for the query.
An observant reader will notice that the actual time numbers don't exactly match the cost estimates. This actually isn't because the estimate was off; it's because the estimate isn't measured in time, it's measured in an arbitrary unit. To be more specific, the units for planner estimates are "How long it takes to sequentially read a single page from disk."
Of course, there's not exactly a lot to analyze in "SELECT * FROM table", so let's try something a bit more interesting…
EXPLAIN SELECT * FROM customer ORDER BY city;
QUERY PLAN
--------------------------------------------------------------------
Sort  (cost=173.12..178.24 rows=2048 width=107)
Sort Key: city
->  Seq Scan on customer  (cost=0.00..60.48 rows=2048 width=107)
Now we see that the query plan includes two steps, a sort and a sequential scan. Although it's may seem counter-intuitive, the data flows from lower steps in the plan to higher steps, so the output of the sequential scan is being fed to the sort operator (well, technically the sort operator is pulling data from the sequential scan).
If you look at the sort step, you will notice that it's telling us what it's sorting on (the "Sort Key"). Many query steps will print out additional information like this. Something else to notice is that the cost to return the first row from a sort operation is very high, nearly the same as the cost to return all the rows. This is because a sort can't return any rows until the data is actually sorted, which is what takes the most time.
Whenever there are multiple query steps, the cost reported in each step includes not only the cost to perform that step, but also the cost to perform all the steps below it. So, in this example, the actual cost of the sort operation is 173.12-60.48 for the first row, or 178.24-60.48 for all rows. Why am I subtracting 60.48 from both the first row and all row costs? Because the sort operation has to obtain all the data from the sequential scan before it can return any data. In general, any time you see a step with very similar first row and all row costs, that operation requires all the data from all the preceding steps.
Let's look at something even more interesting…
EXPLAIN ANALYZE SELECT * FROM customer JOIN contact USING (last_name);
QUERY PLAN
------------------------------------------------------------------------------------------------------------
Hash Join  (cost=1.02..92.23 rows=2048 width=351) (actual time=1.366..58.684 rows=4096 loops=1)
Hash Cond: (("outer".last_name)::text = ("inner".last_name)::text)
->  Seq Scan on customer  (cost=0.00..60.48 rows=2048 width=107) (actual time=0.079..21.658 rows=2048 loops=1)
->  Hash  (cost=1.02..1.02 rows=2 width=287) (actual time=0.146..0.146 rows=2 loops=1)
->  Seq Scan on contact  (cost=0.00..1.02 rows=2 width=287)
(actual time=0.074..0.088 rows=2 loops=1)
Total runtime: 62.233 ms
Now, something we can sink our teeth into! Notice how there's some indentation going on. Indentation is used to show what query steps feed into other query steps. Here we can see that the hash join is fed by a sequential scan and a hash operation. That hash operation is itself fed by another sequential scan. Notice that the hash operation has the same cost for both first and all rows; it needs all rows before it can return any rows. This becomes interesting in this plan when you look at the hash join: the first row cost reflects the total row cost for the hash, but it reflects the first row cost of 0.00 for the sequential scan on customer. That's because a hash join can start returning rows as soon as it gets the first row from both of its inputs.
I promised to get back to what loops meant, so here's an example:
->  Nested Loop  (cost=5.64..14.71 rows=1 width=140) (actual time=18.983..19.481 rows=4 loops=1)
->  Hash Join  (cost=5.64..8.82 rows=1 width=72) (actual time=18.876..19.212 rows=4 loops=1)
->  Index Scan using pg_class_oid_index on pg_class i  (cost=0.00..5.88 rows=1 width=72)
(actual time=0.051..0.055 rows=1 loops=4)
A nested loop is something that should be familiar to procedural coders; it works like this:
for each row in input_a
for each row in input_b
do something
next
next
So, if there are 4 rows in input_a, input_b will be read in its entirety 5 times. Put another way, it will be looped through 4 times. This is what the query plan section above is showing. If you do the math, you'll see that 0.055 * 4 accounts for most of the difference between the total time of the hash join and the total time of the nested loop (the remainder is likely the overhead of measuring all of this).
So, what's this all mean in "real life"? Typically, if you're running EXPLAIN on a query it's because you're trying to improve its performance. The key to this is to identify the step that is taking the longest amount of time and see what you can do about it. Let's walk through the following example and identify what the "problem step" is. (This is a query anyone with an empty database should be able to run and get the same output).
EXPLAIN ANALYZE SELECT * FROM pg_indexes WHERE tablename='pg_constraint';
QUERY PLAN
---------------------------------------------------------------------------------------------------------------
Nested Loop Left Join  (cost=5.64..16.89 rows=1 width=260) (actual time=19.552..20.530 rows=4 loops=1)
Join Filter: ("inner".oid = "outer".reltablespace)
->  Nested Loop Left Join  (cost=5.64..15.84 rows=1 width=200) (actual time=19.313..20.035 rows=4 loops=1)
Join Filter: ("inner".oid = "outer".relnamespace)
->  Nested Loop  (cost=5.64..14.71 rows=1 width=140) (actual time=18.983..19.481 rows=4 loops=1)
->  Hash Join  (cost=5.64..8.82 rows=1 width=72) (actual time=18.876..19.212 rows=4 loops=1)
Hash Cond: ("outer".indrelid = "inner".oid)
->  Seq Scan on pg_index x  (cost=0.00..2.78 rows=78 width=8)
(actual time=0.037..0.296 rows=80 loops=1)
->  Hash  (cost=5.63..5.63 rows=1 width=72)
(actual time=18.577..18.577 rows=1 loops=1)
->  Index Scan using pg_class_relname_nsp_index on pg_class c
(cost=0.00..5.63 rows=1 width=72)
(actual time=18.391..18.464 rows=1 loops=1)
Index Cond: (relname = 'pg_constraint'::name)
Filter: (relkind = 'r'::"char")
->  Index Scan using pg_class_oid_index on pg_class i  (cost=0.00..5.88 rows=1 width=72)
(actual time=0.051..0.055 rows=1 loops=4)
Index Cond: (i.oid = "outer".indexrelid)
Filter: (relkind = 'i'::"char")
->  Seq Scan on pg_namespace n  (cost=0.00..1.06 rows=6 width=68)
(actual time=0.014..0.045 rows=6 loops=4)
->  Seq Scan on pg_tablespace t  (cost=0.00..1.02 rows=2 width=68)
(actual time=0.010..0.018 rows=2 loops=4)
Total runtime: 65.294 ms
The nested loop has most of the cost, with a runtime of 20.035 ms. That nested loop is also pulling data from a nested loop and a sequential scan, and again the nested loop is where most of the cost is (with 19.481 ms total time).
So far, our "expensive path" looks like this:
Nested Loop Left Join  (cost=5.64..16.89 rows=1 width=260) (actual time=19.552..20.530 rows=4 loops=1)
Join Filter: ("inner".oid = "outer".reltablespace)
->  Nested Loop Left Join  (cost=5.64..15.84 rows=1 width=200) (actual time=19.313..20.035 rows=4 loops=1)
Join Filter: ("inner".oid = "outer".relnamespace)
->  Nested Loop  (cost=5.64..14.71 rows=1 width=140) (actual time=18.983..19.481 rows=4 loops=1)
In this example, all of those steps happen to appear together in the output, but that won't always happen.
The lowest nested loop node pulls data from the following:
->  Hash Join  (cost=5.64..8.82 rows=1 width=72) (actual time=18.876..19.212 rows=4 loops=1)
Hash Cond: ("outer".indrelid = "inner".oid)
->  Seq Scan on pg_index x  (cost=0.00..2.78 rows=78 width=8)
(actual time=0.037..0.296 rows=80 loops=1)
->  Hash  (cost=5.63..5.63 rows=1 width=72) (actual time=18.577..18.577 rows=1 loops=1)
->  Index Scan using pg_class_relname_nsp_index on pg_class
(cost=0.00..5.63 rows=1 width=72) (actual time=18.391..18.464 rows=1 loops=1)
Index Cond: (relname = 'pg_constraint'::name)
Filter: (relkind = 'r'::"char")
->  Index Scan using pg_class_oid_index on pg_class i  (cost=0.00..5.88 rows=1 width=72)
(actual time=0.051..0.055 rows=1 loops=4)
Index Cond: (i.oid = "outer".indexrelid)
Filter: (relkind = 'i'::"char")
Here we can see that the hash join has most of the time. It's pulling from a sequential scan and a hash. That hash has most of the time:
->  Hash  (cost=5.63..5.63 rows=1 width=72) (actual time=18.577..18.577 rows=1 loops=1)
->  Index Scan using pg_class_relname_nsp_index on pg_class c
(cost=0.00..5.63 rows=1 width=72) (actual time=18.391..18.464 rows=1 loops=1)
Index Cond: (relname = 'pg_constraint'::name)
Filter: (relkind = 'r'::"char")
Finally, we get to the most expensive part of the query: the index scan on pg_class_relname_nsp_index. Unfortunately for us, it will be virtually impossible to speed up an index scan that only reads a single row. But also note that it only takes 18.464 ms; it's unlikely that you'll ever find yourself trying to improve performance at that level.
One final thing to note: the measurement overhead of EXPLAIN ANALYZE is non-trivial. In extreme cases it can account for 30% or more of query execution time. Just remember that EXPLAIN is a tool for measuring relative performance, and not absolute performance.
Unfortunately, EXPLAIN is something that is poorly documented in the PostgreSQL manual. I hope this article sheds some light on this important tuning tool.
Aggregates — Why are min(), max(), and count() so slow?
A common complaint against PostgreSQL is the speed of its aggregates. People often ask why count(*) or min/max are slower than on some other database. There are actually two problems here, one that's easy to fix and one that isn't so easy.
The ORDER BY / LIMIT Hack
Prior to version 8.1, the query planner didn't know that you could use an index to handle min or max, so it would always table-scan. Fortunately, you can work around this by doing
-- Find minimum value for field
SELECT field FROM table WHERE field IS NOT NULL ORDER BY field ASC LIMIT 1;

-- Find maximum value for field
SELECT field FROM table WHERE field IS NOT NULL ORDER BY field DESC LIMIT 1;
Of course that's a bit of a pain, so in 8.1 the planner was changed so that it will make that substitution on the fly. Unfortunately, it's not perfect; while writing this article I discovered that SELECT max() on a field with a lot of NULL values will take a long time, even if it's using an index on that field. If you try the ORDER BY / LIMIT hack, it is equally slow. I suspect this is because the database has to scan past all the NULL values. In fact, if you create an index on the field and exclude NULL values from that index, the ORDER BY / LIMIT hack will use that index and return very quickly. But a simple max() on that field will continue using the index with NULLs in it.
COUNT(*)
The second problem isn't easy to solve. If you've read my past articles you'll recall that PostgreSQL's MVCC (Multi-Version Concurrency Control) does away with the need for expensive read locks by keeping multiple versions of table rows that have been updated, and not immediately removing deleted rows. This is done by storing 'visibility information' in each row. But for performance reasons, this information is not stored in indexes. This means that every time a row is read from an index, the engine has to also read the actual row in the table to ensure that the row hasn't been deleted.
On the other hand, many other databases do not have this requirement; if a row is in the index then it's a valid row in the table. This allows those databases to do what's known as 'index covering'. Simply put, if all the information a query needs is in an index, the database can get away with reading just the index and not reading the base table at all, providing much higher performance.
If you are using count(*), the database is free to use any column to count, which means it can pick the smallest covering index to scan (note that this is why count(*) is much better than count(some_field), as long as you don't care if null values of some_field are counted). Since indexes often fit entirely in memory, this means count(*) is often very fast.
But as I mentioned, PostgreSQL must read the base table any time it reads from an index. This means that, no matter what, SELECT count(*) FROM table; must read the entire table. Fortunately, there are plans in the works for 8.2 that will allow partial index covering. In a nutshell, the database will keep track of table pages that are known not to contain any deleted rows. With that information available, the engine will be able to tell very quickly if it needs to look at the base table for any given row that it reads out of an index. This means that tables that don't see a lot of updates or deletes will see index scan performance that is close to what you would get on databases that can do true index covering.
Aside from that nice performance improvement for 8.2, there are still ways you might be able to improve your performance if you're currently using count(*). The key is to consider why you are using count(*) in the first place. Do you really need an exact count? In many cases, you don't. count(*) is arguably one of the most abused database functions there is. I've seen it used in many cases where there was no need. Perhaps the worst is as a means to see if a particular row exists, IE:
SELECT count(*) INTO variable FROM table WHERE condition;
IF variable > 0 THEN
...
END IF;
There's no reason you need an exact count here. Instead, try
IF EXISTS( SELECT * FROM table WHERE condition ) THEN
Or, if you're using an external language (though if you're doing this in an external language you should also be asking yourself if you should instead write a stored procedure...):
SELECT 1 INTO dummy WHERE EXISTS( SELECT * FROM table WHERE condition );
IF FOUND THEN
...
END IF;
Note that in this example you'll either get one row back or no rows back.
Maybe you're working on something where you actually need a count of some kind.
In that case, consider using an estimate. Google is a perfect example of this.
Ever noticed how when you search for something the results page shows that you're viewing "results 1-10 of about 728,000"? This is because there's no reason to provide an exact number.
How do you obtain estimates for count(*)? If you just want to know the approximate number of rows in a table you can simply select out of pg_class:
SELECT reltuples FROM pg_class WHERE oid = 'schemaname.tablename'::regclass::oid;
The number returned is an estimate of the number of tables in the table at the time of the last ANALYZE.
If you want an estimate of the number of rows that will be returned from an arbitrary query you unfortunately need to parse the output of explain.
Finally, if you have to have an exact count and performance is an issue you can build a summary table that contains the number of rows in a table. There are two ways to do this. The simplest is to create a trigger or rule that will update the summary table every time rows are inserted or deleted:
http://www.varlena.com/varlena/GeneralBits/49.php
is an example of how to do that. The downside to this approach is that it forces all inserts and deletes on a table you're keeping a count on to serialize. This is because only one transaction can update the appropriate row in the rowcount table at a time.
A variant of this that removes the serialization is to keep a 'running tally' of rows inserted or deleted from the table. Because that running tally only needs to insert into the tally table multiple transactions can update the table you're keeping a count on at the same time. The downside is that you must periodically clear the tally table out. A summary if this technique can be found at
http://archives.postgresql.org/pgsql-performance/2004-01/msg00059.php
.
Of course, neither of these tricks helps you if you need a count of something other than an entire table, but depending on your requirements you can alter either technique to add constraints on what conditions you count on.
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
