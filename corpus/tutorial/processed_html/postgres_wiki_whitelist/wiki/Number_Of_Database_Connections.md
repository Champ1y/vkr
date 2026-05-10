---
title: "Number Of Database Connections - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Number_Of_Database_Connections.html"
source_url: "https://wiki.postgresql.org/wiki/Number_Of_Database_Connections"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# Number Of Database Connections - PostgreSQL wiki

Number Of Database Connections - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Number Of Database Connections
Jump to navigation
Jump to search
You can often support more concurrent users by reducing the number of database connections and using some form of connection pooling.  This page attempts to explain why that is.
Summary
A database server only has so many resources, and if you don't have enough connections active to use all of them, your throughput will generally improve by using more connections.  Once all of the resources are in use, you won't push any more work through by having more connections competing for the resources.  In fact, throughput starts to fall off due to the overhead from that contention.  You can generally improve both latency and throughput by limiting the number of database connections with active transactions to match the available number of resources, and queuing any requests to start a new database transaction which come in while at the limit.
Contrary to many people's initial intuitive impulses, you will often see a transaction
reach completion sooner
if you queue it when it is ready but the system is busy enough to have saturated resources and
start it later
when resources become available.
Pg will usually complete the same 10,000 transactions faster by doing them 5, 10 or 20 at a time than by doing them 500 at a time. Determining exactly how many should be done at once varies by workload and requires tuning.
The Need for an External Pool
If you look at any graph of PostgreSQL performance with number of connections on the
x
axis and tps on the
y
access (with nothing else changing), you will see performance climb as connections rise until you hit saturation, and then you have a "knee" after which performance falls off.  A lot of work has been done for version 9.2 to push that knee to the right and make the fall-off more gradual, but the issue is intrinsic -- without a built-in connection pool or at least an admission control policy, the knee and subsequent performance degradation will always be there.
The decision not to include a connection pooler inside the PostgreSQL server itself has been taken deliberately and with good reason:
In many cases you will get better performance if the connection pooler is running on a separate machine;
There is no single "right" pooling design for all needs, and having pooling outside the core server maintains flexibility;
You can get improved functionality by incorporating a connection pool into client-side software; and finally
Some client side software (like Java EE / JPA / Hibernate) always pools connections, so built-in pooling in PostgreSQL would then be wasteful duplication.
Many frameworks do the pooling in a process running on the the database server machine (to minimize latency effects from the database protocol) and accept high-level requests to run a certain function with a given set of parameters, with the entire function running as a single database transaction. This ensures that network latency or connection failures can't cause a transaction to hang while waiting for something from the network, and provides a simple way to retry any database transaction which rolls back with a serialization failure (SQLSTATE 40001 or 40P01).
Since a pooler built in to the database engine would be inferior (for the above reasons), the community has decided not to go that route.
If your client software does not have built-in connection pooling facilities, there are several
external pooling options available
. Persisistent connections (as maintained by Apache's mod_php, for example) are *not* pooling and still require a connection pool.
Reasons for Performance Reduction Past the "Knee"
There are a number of independent reasons that performance falls off with more database connections.
Disk contention
.  If you need to go to disk for random access (ie your data isn't cached in RAM), a large number of connections can tend to force more tables and indexes to be accessed at the same time, causing heavier seeking all over the disk. Seeking on rotating disks is massively slower than sequential access so the resulting "thrashing" can slow systems that use traditional hard drives down a lot.
RAM usage
.  The work_mem setting can have a big impact on performance.  If it is too small, hash tables and sorts spill to disk, bitmap heap scans become "lossy", requiring more work on each page access, etc.  So you want it to be big.  But work_mem RAM can be allocated for each node of a query on each connection, all at the same time.  So a big work_mem with a large number of connections can cause a lot of the OS cache to be periodically discarded, forcing more accesses to disk; or it could even put the system into swapping.  So the more connections you have, the more you need to make a choice between slow plans and trashing cache/swapping.
Lock contention
.  This happens at various levels: spinlocks, LW locks, and all the locks that show up in pg_locks.  As more processes compete for the spinlocks (which protect LW locks acquisition and release, which in turn protect the heavyweight and predicate lock acquisition and release) they account for a high percentage of CPU time used.
Context switches
.  The processor is interrupted from working on one query and has to switch to another, which involves saving state and restoring state.  While the core is busy swapping states it is not doing any useful work on any query. Context switches are much cheaper than they used to be with modern CPUs and system call interfaces but are still far from free.
Cache line contention
.  One query is likely to be working on a particular area of RAM, and the query taking its place is likely to be working on a different area; causing data cached on the CPU chip to be discarded, only to need to be reloaded to continue the other query.  Besides that the various processes will be grabbing control of cache lines from each other, causing stalls.  (Humorous note, in one oprofile run of a heavily contended load, 10% of CPU time was attributed to a 1-byte noop; analysis showed that it was because it needed to wait on a cache line for the following machine code operation.)
General scaling
.  Some internal structures allocated based on max_connections scale at O(N^2) or O(N*log(N)).  Some types of overhead which are negligible at a lower number of connections can become significant with a large number of connections.
How to Find the Optimal Database Connection Pool Size
A formula which has held up pretty well across a lot of benchmarks for years is that for optimal throughput the number of active connections should be somewhere near ((
core_count
* 2) +
effective_spindle_count
).  Core count should not include HT threads, even if hyperthreading is enabled.  Effective spindle count is zero if the active data set is fully cached, and approaches the actual number of spindles as the cache hit rate falls.  Benchmarks of WIP for version 9.2 suggest that this formula will need adjustment on that release.  There hasn't been any analysis so far regarding how well the formula works with SSDs.
However you choose a starting point for a connection pool size, you should probably try incremental adjustments with your production system to find the actual "sweet spot" for your hardware and workload.
Remember that this "sweet spot" is for the number of connections that are
actively doing work
. Ignore mostly-idle connections used for system monitoring and control when working out an appropriate pool size. You should always make
max_connections
a bit bigger than the number of connections you enable in your connection pool. That way there are always a few slots available for direct connections for system maintenance and monitoring.
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
