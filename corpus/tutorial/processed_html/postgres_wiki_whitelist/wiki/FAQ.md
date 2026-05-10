---
title: "FAQ - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/FAQ.html"
source_url: "https://wiki.postgresql.org/wiki/FAQ"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# FAQ - PostgreSQL wiki

FAQ - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
FAQ
Jump to navigation
Jump to search
Additional FAQ Entries on this Wiki
Translations of this Document
German
Portuguese
Spanish
Русский
עברית
Platform-specific questions
Windows users should also read the
platform FAQ for Windows
. There are
FAQs for other platforms
too.
General Questions
What is PostgreSQL? How is it pronounced? What is Postgres?
PostgreSQL is pronounced Post-Gres-Q-L. (For those curious about how
to say "PostgreSQL", an
audio file
is available.)
PostgreSQL is an object-relational database system that has the
features of traditional proprietary database systems with enhancements
to be found in next-generation DBMS systems. PostgreSQL is free and
the complete source code is available.
PostgreSQL development is performed by a team of mostly volunteer
developers spread throughout the world and communicating via the
Internet. It is a community project and is not controlled by any
company. To get involved, see the
Developer FAQ
.
Postgres is a widely-used nickname for PostgreSQL. It was the original
name of the project at Berkeley and is strongly preferred over other
nicknames. If you find 'PostgreSQL' hard to pronounce, call it
'Postgres' instead.
Who controls PostgreSQL?
If you are looking for a PostgreSQL gatekeeper, central committee, or
controlling company, give up --- there isn't one. We do have a core
committee and git committers, but these groups are more for
administrative purposes than control. The project is directed by the
community of developers and users, which anyone can join. All you need
to do is subscribe to the mailing lists and participate in the
discussions. (See the
Developer's FAQ
for information on how to get
involved in PostgreSQL development.)
Who is the PostgreSQL Global Development Group?
The "PGDG" is an international, unincorporated association of
individuals and companies who have contributed to the PostgreSQL
project.  The PostgreSQL Core Team generally act as spokespeople
for the PGDG.
Who is the PostgreSQL Core Team?
The core team
members
are senior contributors to
PostgreSQL who perform specific
roles
for the project.
What about the various PostgreSQL foundations?
While the PostgreSQL project utilizes non-profit corporations in the
USA, Europe, Brazil and Japan for fundraising and project coordination,
these entities do not own the PostgreSQL code.
What is the license of PostgreSQL?
PostgreSQL is distributed under a license similar to BSD and MIT. Basically, it
allows users to do anything they want with the code, including
reselling binaries without the source code. The only restriction is
that you not hold us legally liable for problems with the software.
There is also the requirement that this copyright appear in all copies
of the software. Here is the license we use:
PostgreSQL Database Management System
(formerly known as Postgres, then as Postgres95)

Portions Copyright (c) 1996-2011, PostgreSQL Global Development Group

Portions Copyright (c) 1994, The Regents of the University of California

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose, without fee, and without a written agreement
is hereby granted, provided that the above copyright notice and this
paragraph and the following two paragraphs appear in all copies.

IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS
DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO
PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
What platforms does PostgreSQL support?
In general, any modern Unix-compatible platform should be able to run
PostgreSQL. The platforms that have received recent explicit testing
can be seen in the
Build farm
.
The documentation contains more details about supported platforms at
http://www.postgresql.org/docs/current/static/supported-platforms.html
.
PostgreSQL also runs natively on Microsoft Windows NT-based operating
systems like Windows XP, Vista, 7, 8, 2003, 2008, etc. A prepackaged installer
is available at
http://www.postgresql.org/download/windows
.
Cygwin builds for Windows exist but are generally not recommended; use the native Windows builds instead. You can use the Cygwin build of the PostgreSQL client library (libpq) to connect to a native Windows PostgreSQL if you really need Cygwin for client applications.
Where can I get PostgreSQL?
There are binary distributions for various operating systems and platforms; see
our download area
.
The source code can be obtained
via web browser
or
through ftp
.
What is the most recent release?
The latest release of PostgreSQL is shown on the front page of
our website
.
We typically have a major release every year, with minor releases every few months.
Minor releases are usually made at the same time for all supported major-release branches.
For more about major versus minor releases, see
http://www.postgresql.org/support/versioning
.
Where can I get support?
The PostgreSQL community provides assistance to many of its users via
email. The main web site to subscribe to the email lists is
http://www.postgresql.org/community/lists/
. The general or bugs lists
are a good place to start. For best results, consider reading the
guide to reporting problems
before you post to make sure you
include enough information for people to help you.
The major IRC channel is #postgresql on Libera (irc.libera.chat).
A Spanish one also
exists on the same network, (#postgresql-es), a French one,
(#postgresqlfr), and a Brazilian one, (#postgresql-br). There is also
a PostgreSQL channel on EFNet.
A list of support companies is available at
http://www.postgresql.org/support/professional_support
.
How do I submit a bug report?
Visit the PostgreSQL bug form at
http://www.postgresql.org/support/submitbug
to submit your bug
report to the pgsql-bugs mailing list. Also check out our ftp
site
ftp://ftp.postgresql.org/pub/
to see if there is a more recent
PostgreSQL version.
For a prompt and helpful response, it is important for you to read the
guide to reporting problems
to make sure that you include the
information required to fully understand and act on your report.
Bugs submitted using the bug form or posted to any PostgreSQL mailing
list typically generates one of the following replies:
It is not a bug, and why
It is a known bug and is already on the TODO list
The bug has been fixed in the current release
The bug has been fixed but is not packaged yet in an official release
A request is made for more detailed information:
Operating system
PostgreSQL version
Reproducible test case
Debugging information
Debugger backtrace output
The bug is new. The following might happen:
A patch is created and will be included in the next major or minor release
The bug cannot be fixed immediately and is added to the TODO list
How do I find out about known bugs or missing features?
PostgreSQL supports an extended subset of SQL:2008. See our
TODO list
for known bugs, missing features, and future plans.
A feature request usually results in one of the following replies:
The feature is already on the TODO list
The feature is not desired because:
It duplicates existing functionality that already follows the SQL standard
The feature would increase code complexity but add little benefit
The feature would be insecure or unreliable
The new feature is added to the TODO list
PostgreSQL does not use a bug tracking system because we find it more
efficient to respond directly to email and keep the TODO list
up-to-date. In practice, bugs don't last very long in the software,
and bugs that affect a large number of users are fixed rapidly. The
only place to find all changes, improvements, and fixes in a
PostgreSQL release is to read the git log messages. Even the release
notes do not list every change made to the software.
A bug I'm encountering is fixed in a newer minor release of PostgreSQL, but I don't want to upgrade. Can I get a patch for just this issue?
No. Nobody will make a custom patch for you so you can (say) extract a fix from 8.4.3 and apply it to 8.4.1 . That's because there should never be any need to do so. If you really feel you have to do this you will need to extract the patch from
the sources
yourself.
PostgreSQL has a strict policy that only bug fixes are back-patched into point releases, as per the
version policy
. It is safe to upgrade from 8.4.1 to 8.4.3,
for example. Binary compatibility will be maintained, no dump and reload is required, nothing will break, but bugs that might
cause problems have been fixed. At worst a bug fix might require a REINDEX after the update, in which case this will be described in the release notes. Even if you are not yet encountering a particular bug, you might later, and it is wise to upgrade promptly.
You just have to install the update and re-start the database server. It's wise to read the release notes but rarely necessary to do anything special.
Upgrading from 8.3 to 8.4, or 8.4 to 9.0, is a major upgrade that does not come with the same guarantees. However, if a bug
is discovered in 9.0 then it will generally be fixed ("back-patched") in all maintained older versions like 8.4 and 8.3 if it is safe and
practical to do so.
This means that if you're running 8.1.0, upgrading to 8.1.21 is
strongly
recommended and very safe. On the other hand,
upgrading to the next major release, 8.2.x, may require changes to your app, and will certainly require a dump and reload or (for 8.4+) pg_upgrade; see
upgrading a PostgreSQL cluster
in the documentation for options.
If you want to be careful about all upgrades, you should read the
release notes
for each point release between your current one and the latest minor version of the same major release carefully. If you're
exceptionally paranoid about upgrades, you can fetch the source code to each set of point release changes from
PostgreSQL's git repository
and examine it.
It is strongly recommended that you
always
upgrade to the latest minor release. Avoid trying to extract and apply individual fixes
from point releases; by doing so you're bypassing all the QA done by the PostgreSQL team when they prepare a release, and are creating your
own custom version that
nobody else has ever used
. It's a lot safer to just update to the latest tested, safe release.
Patching your own custom, non-standard build will also take more time/effort, and will require the same amount of downtime as a normal upgrade.
I have a program that says it wants PostgreSQL x.y.1. Can I use PostgreSQL x.y.2 instead?
Any program that works with a particular version, like 8.4.1, should work with any other minor version in the same major version. That means that if a program says it wants (eg) 8.4.1, you can and should install the latest in the 8.4 series instead.
If your application vendor tells you otherwise please direct them to this FAQ and, if they're still unconvinced, get in touch with the pgsql-general mailing list so we can contact them. Forcing users to stay on old minor releases is dangerous for security and data integrity.
See the previous question for more details.
What documentation is available?
PostgreSQL includes extensive documentation, including a large manual,
manual pages, and some test examples. See the /doc directory. You can
also browse the manuals online at
http://www.postgresql.org/docs
.
There are a number of PostgreSQL
books available for purchase; two of them are also available online.  A list of books can be found at
http://www.postgresql.org/docs/books/
.  One of the most popular ones is the one by Korry & Susan
Douglas.
There is also a collection of
PostgreSQL technical articles on the
wiki
.
The command line client program psql has some \d commands to show
information about types, operators, functions, aggregates, etc. - use
\? to display the available commands.
How can I learn SQL?
First,  consider the PostgreSQL-specific books mentioned above. Many of
our users also like The Practical SQL Handbook, Bowman, Judith S., et
al., Addison-Wesley. Others like The Complete Reference SQL, Groff et
al., McGraw-Hill.
Many people consider the PostgreSQL documentation to be an excellent guide
for learning SQL its self, as well as for PostgreSQL's implementation of it.
For best results use PostgreSQL alongside another full-featured SQL database as
you learn, so you get used to SQL without becoming reliant on PostgreSQL-specific
features. The PostgreSQL documentation generally mentions when features are PostgreSQL
extensions of the standard.
There are also many nice tutorials available online:
http://sqlcourse.com
http://www.w3schools.com/sql/default.asp
http://sqlzoo.net
https://blog.devart.com/postgresql-tutorial.html
How do I submit a patch or join the development team?
See the
Developer's FAQ
.
How does PostgreSQL compare to other DBMSs?
There are several ways of measuring software: features, performance,
reliability, support, and price.
Features
PostgreSQL has most features present in large proprietary DBMSs,
like transactions, subselects, triggers, views, foreign key
referential integrity, and sophisticated locking.
We have some
features they do not have, like user-defined types,
inheritance, rules, and multi-version concurrency control to
reduce lock contention.
Other features (
geospacial
capabilities,
temporal
capabilities,
GUI interfaces
, etc.) are available via 3rd parties or
PostgeSQL supplied extensions
.
Performance
PostgreSQL's performance is comparable to other proprietary and
open source databases. It is faster for some things, slower for
others. Our performance is usually +/-10% compared to other databases.
Reliability
We realize that a DBMS must be reliable, or it is worthless. We
strive to release well-tested, stable code that has a minimum
of bugs. Each release has at least one month of beta testing,
and our release history shows that we can provide stable, solid
releases that are ready for production use. We believe we
compare favorably to other database software in this area.
Support
Our mailing lists provide contact with a large group of
developers and users to help resolve any problems encountered.
While we cannot guarantee a fix, proprietary DBMSs do not always
supply a fix either. Direct access to developers, the user
community, manuals, and the source code often make PostgreSQL
support superior to other DBMSs. There is commercial
per-incident support available for those who need it. (See
section 1.7
).
Price
We are free for all use, both proprietary and open source.
You can add our code to your product with no limitations,
except those outlined in our BSD-style license stated above.
Can PostgreSQL be embedded?
PostgreSQL is designed as a client/server architecture, which requires
separate processes for each client and server, and various helper
processes. Many embedded architectures can support such requirements.
However, if your embedded architecture requires the database server to
run inside the application process, you cannot use Postgres and should
select a lighter-weight database solution.
Popular embeddable options include
SQLite
and
Firebird SQL
.
How do I unsubscribe from the PostgreSQL email lists? How do I avoid receiving duplicate emails?
The PostgreSQL Majordomo page allows subscribing or unsubscribing from
any of the PostgreSQL email lists. (You might need to have your
Majordomo password emailed to you to log in.)
All PostgreSQL email lists are configured so a group reply goes to the
email list and the original email author. This is done so users
receive the quickest possible email replies. If you would prefer not
to receive duplicate email from the list in cases where you already
receive an email directly, check eliminatecc from the Majordomo Change
Settings page. You can also prevent yourself from receiving copies of
emails you post to the lists by unchecking selfcopy.
User Client Questions
What interfaces are available for PostgreSQL?
The core PostgreSQL source code includes only the C and embedded C interfaces.
All other interfaces are independent projects that are downloaded
separately; being separate allows them to have their own release
schedule and development teams.
Many PostgreSQL installers bundle language client interfaces like PgJDBC, nPgSQL, the Pg ruby gem, psycopg2 for Python, DBD::Pg for Perl, etc into the PostgreSQL installer or offer to download them for you. Additionally, some programming language runtimes come with PostgreSQL client libraries pre-installed.
On Linux systems you can generally just install language bindings like psycopg2 using your package manager.
What tools are available for using PostgreSQL with Web pages?
A nice introduction to Database-backed Web pages can be seen at:
http://www.webreview.com
For Web integration, PHP (
http://www.php.net
) is an excellent
interface.
For complex cases, many use the Perl and DBD::Pg with CGI.pm or
mod_perl.
Does PostgreSQL have a graphical user interface?
There are a large number of GUI Tools that are available for
PostgreSQL from both proprietary and open source developers. A detailed
list can be found in the
Community Guide to PostgreSQL GUI Tools
.
Many installers bundle the graphical
PgAdmin-III
client with the installer, either use
Ecosystem:dbForge Studio for PostgreSQL
.
Administrative Questions
When installing from source code, how do I install PostgreSQL somewhere other than /usr/local/pgsql?
Specify the --prefix option when running configure.
I'm installing PostgreSQL on Windows or OS X and don't know the password for the postgres user
Dave Page wrote a
blog post
explaining what the different passwords are used for, and how to overcome common problems such as resetting them.
PostgreSQL 9.2 now runs as NETWORKSERVICE on Windows so it doesn't need a service account password anymore, it only has the password for the "postgres" database user.
How do I control connections from other hosts?
By default, PostgreSQL only allows connections from the local machine
using Unix domain sockets or TCP/IP connections. Other machines will
not be able to connect unless you modify listen_addresses in the
postgresql.conf file, enable host-based authentication by modifying
the $PGDATA/pg_hba.conf file, and restart the database server.
How do I tune the database engine for better performance?
There are three major areas for potential performance improvement:
Query Changes
This involves modifying queries to obtain better performance:
Creation of indexes, including expression and partial indexes
Use of COPY instead of multiple INSERTs
Grouping of multiple statements into a single transaction to reduce commit overhead
Use of CLUSTER when retrieving many rows from an index
Use of LIMIT for returning a subset of a query's output
Use of Prepared queries
Use of ANALYZE to maintain accurate optimizer statistics
Regular use of VACUUM or pg_autovacuum
Dropping of indexes during large data changes
Server Configuration
A number of postgresql.conf settings affect performance. For
more details, see Administration Guide/Server Run-time
Environment/Run-time Configuration.
Hardware Selection
The effect of hardware on performance is detailed at
http://momjian.us/main/writings/pgsql/hw_performance/index.html
.
What debugging features are available?
There are many log_* server configuration variables at
http://www.postgresql.org/docs/current/interactive/runtime-config-logging.html
that enable printing of query and process statistics which can be very useful for debugging and performance measurements.
Why do I get "Sorry, too many clients" when trying to connect?
You have reached the default limit of 100 database sessions. See
Number of database connections
for advice on whether you should raise the connection limit or add a connection pooler.
What is the upgrade process for PostgreSQL?
See
http://www.postgresql.org/support/versioning
for a general
discussion about upgrading, and
http://www.postgresql.org/docs/current/static/upgrading.html
for specific instructions on upgrading a PostgreSQL cluster.
If you used an installer, check to see if there are specific instructions related to the PostgreSQL installer you used.
Will PostgreSQL handle recent daylight saving time changes in various countries?
PostgreSQL releases 8.0 and up depend on the widely-used tzdata database
(also called the zoneinfo database or the
Olson timezone database
) for
daylight savings information.  To deal with a DST law change that affects you,
install a new tzdata file set and restart the server.
All PostgreSQL update releases include the latest available tzdata files,
so keeping up-to-date on minor releases for your major version is usually
sufficient for this.
On platforms that receive regular software updates including new tzdata files,
it may be more convenient to rely on the system's copy of the tzdata files.
This is possible as a compile-time option.  Most Linux distributions choose
this approach for their pre-built versions of PostgreSQL.
PostgreSQL releases before 8.0 always relied on the operating system's timezone
information.
What computer hardware should I use?
Because PC hardware is mostly compatible, people tend to believe that
all PC hardware is of equal quality. It is not. ECC RAM, good quality hard drives/SSDs, reliable power supplies, and
quality motherboards are more reliable and have better performance
than less expensive hardware. PostgreSQL will run on almost any
hardware, but if reliability and performance are important it is wise
to research your hardware options thoroughly.
Database servers, unlike many other applications, are usually I/O and memory constrained, so it is wise to focus on the I/O subsystem first, then memory capacity, and lastly consider CPU issues.  A good quality, high performance SSD is often the cheapest way to improve database performance. Our email lists can be used to discuss hardware options and tradeoffs.
How does PostgreSQL use CPU resources?
The PostgreSQL server is process-based (not threaded).  Each database session connects to a single PostgreSQL operating system (OS) process.  Multiple sessions are automatically spread across all available CPUs by the OS.  The OS also uses CPUs to handle disk I/O and run other non-database tasks.
Client applications can use threads, each of which connects to a separate database process.
Since version 9.6, portions of some queries can be run in parallel, in separate OS processes, allowing use of multiple CPU cores.
Parallel queries are enabled by default in version 10 (max_parallel_workers_per_gather), with additional parallelism expected in future releases.
Why does PostgreSQL have so many processes, even when idle?
As noted in
the answer above
, PostgreSQL is process based, so it starts one
postgres
(or
postgres.exe
on Windows) instance per connection. The postmaster (which accepts connections and starts new postgres instances for them) is always running. In addition, PostgreSQL generally has one or more "helper" processes like the stats collector, background writer, autovacuum daemon, walsender, etc, all of which show up as "postgres" instances in most system monitoring tools.
Despite the number of processes, they actually use very little in the way of real resources. See
the next answer
.
Why does PostgreSQL use so much memory?
Despite appearances, this is absolutely normal, and there's actually nowhere near as much memory being used as tools like
top
or the Windows process monitor say PostgreSQL is using.
Tools like
top
and the Windows process monitor may show many
postgres
instances (see above), each of which appears to use a huge amount of memory. Often, when added up, the amount the postgres instances use is many times the amount of memory actually installed in the computer!
This is a consequence of how these tools report memory use. They generally don't understand shared memory very well, and show it as if it was memory used individually and exclusively by each postgres instance. PostgreSQL uses a big chunk of shared memory to communicate between its backends and cache data. Because these tools count that shared memory block once per
postgres
instance instead of counting it once for
all
postgres
instances, they massively over-estimate how much memory PostgreSQL is using.
Furthermore, many versions of these tools don't report the entire shared memory block as being used by an individual instance immediately when it starts, but rather count the number of shared pages it has touched since starting.  Over the lifetime of an instance, it will inevitably touch more and more of the shared memory until it has touched every page, so that its reported usage will gradually rise to include the entire shared memory block.  This is frequently misinterpreted to be a memory leak; but it is no such thing, only a reporting artifact.
Operational Questions
How do I SELECT only the first few rows of a query? A random row?
To retrieve only a few rows, if you know at the number of rows needed
at the time of the SELECT use LIMIT . If an index matches the ORDER BY
it is possible the entire query does not have to be executed. If you
don't know the number of rows at SELECT time, use a cursor and FETCH.
To SELECT a random row, use:
SELECT col
FROM tab
ORDER BY random()
LIMIT 1;
See also this
blog entry by Andrew Gierth
that has more information on this topic.
How do I find out what tables, indexes, databases, and users are defined? How do I see the queries used by psql to display them?
Use the \dt command to see tables in psql. For a complete list of
commands inside psql you can use \?. Alternatively you can read the
source code for psql in file pgsql/src/bin/psql/describe.c, it
contains SQL commands that generate the output for psql's backslash
commands. You can also start psql with the -E option so it will print
out the queries it uses to execute the commands you give. PostgreSQL
also provides an SQL compliant INFORMATION SCHEMA interface you can
query to get information about the database.
There are also system tables beginning with pg_ that describe these
too.
Use psql -l will list all databases.
Also try the file pgsql/src/tutorial/syscat.source. It illustrates
many of the SELECTs needed to get information from the database system
tables.
How do you change a column's data type?
Changing the data type of a column can be done easily in 8.0 and later
with ALTER TABLE ALTER COLUMN TYPE.
In earlier releases, do this:
BEGIN;
ALTER TABLE tab ADD COLUMN new_col new_data_type;
UPDATE tab SET new_col = CAST(old_col AS new_data_type);
ALTER TABLE tab DROP COLUMN old_col;
COMMIT;
You might then want to do VACUUM FULL tab to reclaim the disk space
used by the expired rows.
What is the maximum size for a row, a table, and a database?
These are the limits:
Maximum size for a database? unlimited (32 TB databases exist)
Maximum size for a table? 32 TB
Maximum size for a row? 400 GB
Maximum size for a field? 1 GB
Maximum number of rows in a table? unlimited
Maximum number of columns in a table? 250-1600 depending on column types
Maximum number of indexes on a table? unlimited
Of course, these are not actually unlimited, but limited to available
disk space and memory/swap space. Performance may suffer when these
values get unusually large.
The maximum table size of 32 TB does not require large file support
from the operating system. Large tables are stored as multiple 1 GB
files so file system size limits are not important.
The maximum table size, row size, and maximum number of columns can be
quadrupled by increasing the default block size to 32k. The maximum
table size can also be increased using table partitioning.
One limitation is that indexes can not be created on columns longer
than about 2,000 characters. Fortunately, such indexes are rarely
needed. Uniqueness is best guaranteed by a function index of an MD5
hash of the long column, and full text indexing allows for searching
of words within the column.
Note if you are storing a table with rows that exceed 2KB in size (aggregate size of data in each
row) then the "Maximum number of rows in a table" may be limited to 4 Billion or less, see
TOAST
.
How much database disk space is required to store data from a typical text file?
A PostgreSQL database may require up to five times the disk space to
store data from a text file.
As an example, consider a file of 100,000 lines with an integer and
text description on each line. Suppose the text string averages
twenty bytes in length. The flat file would be 2.8 MB. The size of the
PostgreSQL database file containing this data can be estimated as 5.2
MB:
24 bytes: each row header (approximate)
24 bytes: one int field and one text field
+ 4 bytes: pointer on page to tuple
----------------------------------------
52 bytes per row
The data page size in PostgreSQL is 8192 bytes (8 KB), so:
8192 bytes per page
-------------------  =  158 rows per database page (rounded down)
52 bytes per row
100000 data rows
------------------  =  633 database pages (rounded up)
158 rows per page
633 database pages * 8192 bytes per page  =  5,185,536 bytes (5.2 MB)
Indexes do not require as much overhead, but do contain the data that
is being indexed, so they can be large also.
NULLs are stored as bitmaps, so they use very little space.
Note that long values may be compressed transparently.
See also this presentation on the topic:
File:How Long Is a String.pdf
.
Why are my queries slow? Why don't they use my indexes?
Indexes are essential to PostgreSQL and are typically used to increase database
performance. Still, indexes mean additional overhead to database systems, which
means they should be applied reasonably. You could check this helful tutorial
to understand their specifics properly to be able to create any particular index
that best suits your particular case
PostgreSQL Indexes
Indexes are not used by every query. Indexes are used only if the
table is larger than a minimum size, and the query selects only a
small percentage of the rows in the table. This is because the random
disk access caused by an index scan can be slower than a straight read
through the table, or sequential scan.
To determine if an index should be used, PostgreSQL must have
statistics about the table. These statistics are collected using
VACUUM ANALYZE, or simply ANALYZE. Using statistics, the optimizer
knows how many rows are in the table, and can better determine if
indexes should be used. Statistics are also valuable in determining
optimal join order and join methods. Statistics collection should be
performed periodically as the contents of the table change.
Indexes are normally not used for ORDER BY or to perform joins. A
sequential scan followed by an explicit sort is usually faster than an
index scan of a large table. However, LIMIT combined with ORDER BY
often will use an index because only a small portion of the table is
returned.
If you believe the optimizer is incorrect in choosing a sequential
scan, use SET enable_seqscan TO 'off' and run query again to see if an
index scan is indeed faster.
When using wild-card operators such as LIKE or ~, indexes can only be
used in certain circumstances:
The beginning of the search string must be anchored to the start of the string, i.e.
LIKE patterns must not start with % or _.
~ (regular expression) patterns must start with ^.
The search string can not start with a character class, e.g. [a-e].
Case-insensitive searches such as ILIKE and ~* do not utilize indexes. Instead, use expression indexes, which are described in
section 4.8
.
C locale must be used during initdb because sorting in a non-C locale often doesn't match the behavior of LIKE. You can create a special text_pattern_ops index that will work in such cases, but note it is only helpful for LIKE indexing.
It is also possible to use full text indexing for word searches.
Note that sometimes indexes are created but marked as "corrupted" and thus not used, see
here
.
The
SlowQueryQuestions
article contains some more tips and guidance.
How do I see how the query optimizer is evaluating my query?
This is done with the EXPLAIN command; see
Using EXPLAIN
. Either you could use a query profiling tool allowing to get the
PostgreSQL execution plan
and query execution statistics in a visual format.
How do I change the sort ordering of textual data?
PostgreSQL sorts textual data according to the ordering that is defined by the current locale, which is selected during initdb.
(In 8.4 and up it will be possible to select a different locale when creating a new database.)
If you don't like the ordering then you need to use a different locale.
In particular, most locales other than "C" sort according to dictionary order, which largely ignores punctuation and spacing.
If that's not what you want then you need "C" locale.
The ~ operator does regular expression matching, and ~* does
case-insensitive regular expression matching. The case-insensitive
variant of LIKE is called ILIKE.
Case-insensitive equality comparisons are normally expressed as:
SELECT *
FROM tab
WHERE lower(col) = 'abc';
This will not use a standard index on "col". However, if you create an
expression index on "lower(col)", it will be used:
CREATE INDEX tabindex ON tab (lower(col));
If the above index is created as UNIQUE, then the column can store
upper and lowercase characters, but it cannot contain identical values that
differ only in case. To force a particular case to be stored in the
column, use a CHECK constraint or a trigger.
In PostgreSQL 8.4 and later, you can also use the contributed
CITEXT data type
, which internally implements the "lower()" calls, so that you can effectively treat it as a fully case-insensitive data type. CITEXT is also
available for 8.3
, and an earlier version that treats only ASCII characters case-insensitively on 8.2 and earlier is available on
pgFoundry
.
In a query, how do I detect if a field is NULL? How do I concatenate possible NULLs? How can I sort on whether a field is NULL or not?
You can test the value with IS NULL or IS NOT NULL, like this:
SELECT *
FROM tab
WHERE col IS NULL;
Concatenating a NULL with something else produces another NULL.
If that's not what you want, you can replace the NULL(s) using
COALESCE(), like this:
SELECT COALESCE(col1, '') || COALESCE(col2, '')
FROM tab;
To sort by the NULL status, use an IS NULL or IS NOT NULL test
in your ORDER BY clause. Things that are true will sort higher than
things that are false, so the following will put NULL entries at the
front of the output:
SELECT *
FROM tab
ORDER BY (col IS NOT NULL), col;
In PostgreSQL 8.3 and up, you can also control sort ordering of NULLs
using the recently-standardized NULLS FIRST/NULLS LAST modifiers,
like this:
SELECT *
FROM tab
ORDER BY col NULLS FIRST;
What is the difference between the various character types?
Type
Internal Name
Notes
VARCHAR(n)
varchar
size specifies maximum length, no padding
CHAR(n)
bpchar
blank-padded to the specified fixed length
TEXT
text
no specific upper limit on length
BYTEA
bytea
variable-length byte array (null-byte safe)
"char" (with the quotes)
char
one byte
You will see the internal name when examining system catalogs and in
some error messages.
The first four types above are "varlena" types (i.e., the field length
is explicitly stored on disk, followed by the data). Thus the actual
space used is slightly greater than the expected size. However, long
values are also subject to compression, so the space on disk might
also be less than expected.
VARCHAR(n) is best when storing variable-length strings if a specific
upper limit on the string length is required by the application.
TEXT is for strings of "unlimited" length (though all fields in PostgreSQL
are subject to a maximum value length of one gigabyte).
CHAR(n) is for storing strings that are all the same length. CHAR(n)
pads with blanks to the specified length, while VARCHAR(n) only stores
the characters supplied.  BYTEA is for storing binary data,
particularly values that include zero bytes. All these types have similar
performance characteristics, except that the blank-padding involved
in CHAR(n) requires additional storage and some extra runtime.
The "char" type (the quotes are required to distinguish it from CHAR(n))
is a specialized datatype that can store exactly one byte.  It is found in
the system catalogs but its use in user tables is generally discouraged.
How do I create a serial/auto-incrementing field?
PostgreSQL supports a SERIAL data type. Actually, this isn't quite
a real type.  It's a shorthand for creating an integer column that
is fed from a sequence.
For example, this:
CREATE TABLE person (
id SERIAL,
name TEXT
);
is automatically translated into this:
CREATE SEQUENCE person_id_seq;
CREATE TABLE person (
id INTEGER NOT NULL DEFAULT nextval('person_id_seq'),
name TEXT
);
The automatically created sequence is named
table
_
serialcolumn
_seq,
where
table
and
serialcolumn
are the names of the table and SERIAL
column, respectively. See the CREATE SEQUENCE manual page for more
information about sequences.
There is also BIGSERIAL, which is like SERIAL except that the resulting
column is of type BIGINT instead of INTEGER.  Use this type if you think
that you might need more than 2 billion serial values over the lifespan
of the table.
Note that sequences may contain "holes" or "gaps" as a normal part of operation. It is entirely normal for generated keys to go 1, 4, 5, 6, 9, ... . See
the FAQ entry on sequence gaps
.
How do I get the value of a SERIAL insert?
The simplest way is to retrieve the assigned SERIAL value with
RETURNING. Using the example table in the previous question, it would look like this:
INSERT INTO person (name) VALUES ('Blaise Pascal') RETURNING id;
You can also call nextval() and use that value in the INSERT, or call
currval() after the INSERT.
Doesn't currval() lead to a race condition with other users?
No. currval() returns the latest sequence value assigned by your session,
independently of what is happening in other sessions.
Why are there gaps in the numbering of my sequence/SERIAL column? Why aren't my sequence numbers reused on transaction abort?
To improve concurrency, sequence values are given out to running
transactions on-demand; the sequence object is not kept locked but is
immediately available for another transaction to get another sequence
value. This causes gaps in numbering from aborted transactions, as documented in the
NOTE section for the nextval() function
.
Additionally, an unclean server shutdown will cause sequences to increment on recovery, because PostgreSQL keeps a cache of sequence numbers to hand out and in an unclean shutdown it isn't sure which of those cached numbers has already been used. Since sequences are allowed to have gaps anyway it takes the safe option and increments the sequence.
Another cause for gaps in sequence is the use of the CACHE clause in
CREATE SEQUENCE
.
In general, you should not rely on SERIAL keys or SEQUENCEs being gapless, nor should you make assumptions about their order;
it is
not
guaranteed that id n+1 was inserted after id n except when both were generated within the same transaction
. Compare synthetic keys for equality and only for equality.
Gap-less sequences are possible, but are very bad for performance. At most one transaction at a time can be inserting rows from a gapless sequence. There is no built-in SERIAL or SEQUENCE equivalent for gap-less sequences, but one is
trivial to implement
. Information on gapless sequence implementations can be found in the mailing list archives, on Stack Overflow, and in
this useful article
. Avoid using a gap-less sequence unless it is an absolute business requirement. Consider dynamically generating the gap-less numbering on demand for display, using the
row_number() window function
, or adding it in a batch process that runs periodically.
See also:
FAQ: Using sequences in PostgreSQL
.
What is an OID?
If a table is created WITH OIDS, each row includes an OID column that is automatically filled in during INSERT.
OIDs are sequentially assigned 4-byte integers.  Initially they are unique
across the entire installation. However, the OID counter wraps around at 4 billion,
and after that OIDs may be duplicated.
It is possible to prevent duplication of OIDs within a single table by
creating a unique index on the OID column (but note that the WITH OIDS
clause doesn't by itself create such an index).
The system checks the index to see if a newly
generated OID is already present, and if so generates a new OID and
repeats.  This works well so long as no OID-containing table has
more than a small fraction of 4 billion rows.
PostgreSQL uses OIDs for object identifiers in the system catalogs,
where the size limit is unlikely to be a problem.
To uniquely number rows in user tables, it is best to use SERIAL
rather than an OID column, or BIGSERIAL if the table is expected to
have more than 2 billion entries over its lifespan.
What is a CTID?
CTIDs identify specific physical rows by their block and
offset positions within a table.
They are used by index entries to point to physical rows.
A logical row's CTID changes when it is updated, so the CTID
cannot be used as a long-term row identifier.  But it is sometimes
useful to identify a row within a transaction when no competing
update is expected.
Why do I get the error "ERROR: Memory exhausted in AllocSetAlloc()"?
You probably have run out of virtual memory on your system, or your
kernel has a low limit for certain resources. Try this before starting
the server:
ulimit -d 262144
limit datasize 256m
Depending on your shell, only one of these may succeed, but it will
set your process data segment limit much higher and perhaps allow the
query to complete. This command applies to the current process, and
all subprocesses created after the command is run. If you are having a
problem with the SQL client because the backend is returning too much
data, try it before starting the client.
How do I tell what PostgreSQL version I am running?
Run this query: SELECT version();
Is there a way to leave an audit trail of database operations?
There's nothing built-in, but it's not too difficult to build such
facilities yourself.
Simple example right in the official docs:
http://www.postgresql.org/docs/current/static/plpgsql-trigger.html#PLPGSQL-TRIGGER-AUDIT-EXAMPLE
Project targeting this feature:
https://www.postgresql.org/ftp/projects/pgFoundry/tablelog/
Background information and other sample implementations:
http://it.toolbox.com/blogs/database-soup/simple-data-auditing-19014
http://www.go4expert.com/forums/showthread.php?t=7252
http://www.alberton.info/postgresql_table_audit.html
How do I create a column that will default to the current time?
Use CURRENT_TIMESTAMP:
CREATE TABLE test (x int, modtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP );
How do I perform an outer join?
PostgreSQL supports outer joins using the SQL standard syntax. Here
are two examples:
SELECT *
FROM t1 LEFT OUTER JOIN t2 ON (t1.col = t2.col);
or
SELECT *
FROM t1 LEFT OUTER JOIN t2 USING (col);
These identical queries join t1.col to t2.col, and also return any
unjoined rows in t1 (those with no match in t2). A RIGHT join would
add unjoined rows of t2. A FULL join would return the matched rows
plus all unjoined rows from t1 and t2. The word OUTER is optional and
is assumed in LEFT, RIGHT, and FULL joins. Ordinary joins are called
INNER joins.
How do I perform queries using multiple databases?
While there is no way to directly query a database other than the current one, there are several approaches to the issue, some of which are described below.
The SQL/MED support in PostgreSQL allows a "foreign data wrapper" to be created, linking tables in a remote database to the local database. The remote database might be another database on the same PostgreSQL instance, or a database half way around the world, it doesn't matter.
postgres_fdw
is built-in to PostgreSQL 9.3 and includes read/write support; a
read-only version for 9.2
can be compiled and installed as a contrib module.
contrib/dblink allows cross-database queries using function calls and is available for much older PostgreSQL versions. Unlike postgres_fdw it can't "push down" conditions to the remote server, so it'll often land up fetching a lot more data than you need.
Of course, a client can also make simultaneous connections to different databases and merge the results on the client side.
How do I return multiple rows or columns from a function?
It is easy using set-returning functions,
Return more than one row of data from PL/pgSQL functions
.
Why do I get "relation with OID ##### does not exist" errors when accessing temporary tables in PL/PgSQL functions?
In PostgreSQL versions < 8.3, PL/PgSQL caches function scripts, and an
unfortunate side effect is that if a PL/PgSQL function accesses a
temporary table, and that table is later dropped and recreated, and
the function called again, the function will fail because the cached
function contents still point to the old temporary table. The solution
is to use EXECUTE for temporary table access in PL/PgSQL. This will
cause the query to be reparsed every time.
This problem does not occur in PostgreSQL 8.3 and later.
What replication solutions are available?
Though "replication" is a single term, there are several technologies
for doing replication, with advantages and disadvantages for each.
Our documentation contains a good introduction to this topic at
http://www.postgresql.org/docs/current/static/high-availability.html
and a
grid listing replication software and features is at
Replication, Clustering, and Connection Pooling
Master/slave replication allows a single master to receive read/write
queries, while slaves can only accept read/SELECT queries. The most
popular freely available master-slave PostgreSQL replication solution
is Slony-I.
Multi-master replication allows read/write queries to be sent to
multiple replicated computers. This capability also has a severe
impact on performance due to the need to synchronize changes between
servers. PGCluster is the most popular such solution freely available
for PostgreSQL.
There are also proprietary and hardware-based replication solutions
available supporting a variety of replication models.
Is possible to create a shared-storage postgresql server cluster?
PostgreSQL does not support clustering using
shared storage
on a SAN, SCSI backplane,
iSCSI volume, or other shared media. Such "RAC-style" clustering isn't supported.
Only replication-based clustering is currently supported.
See
Replication, Clustering, and Connection Pooling
information for details.
Shared-storage
'failover' is possible, but it is not safe to have more than one
postmaster running and accessing the data store at the same time. Heartbeat and
STONITH
or some other hard-disconnect option are recommended.
Why are my table and column names not recognized in my query? Why is capitalization not preserved?
The most common cause of unrecognized names is the use of
double-quotes around table or column names during table creation. When
double-quotes are used, table and column names (called identifiers)
are stored case-sensitive, meaning you must use double-quotes when
referencing the names in a query. Some interfaces, like pgAdmin,
automatically double-quote identifiers during table creation. So, for
identifiers to be recognized, you must either:
Avoid double-quoting identifiers when creating tables
Use only lowercase characters in identifiers
Double-quote identifiers when referencing them in queries
I lost the database password.  What can I do to recover it?
You can't.  However, you can reset it to something else.  To do this, you
edit pg_hba.conf to allow
trust
authorization temporarily
Reload the config file (pg_ctl reload)
Connect and issue ALTER ROLE / PASSWORD to set the new password
edit pg_hba.conf again and restore the previous settings
Reload the config file again
Does PostgreSQL have stored procedures?
PostgreSQL doesn't. However PostgreSQL have very powerful functions and user-defined functions capabilities that can do most things that other RDBMS stored routines (procedures and functions) can do and in many cases more.
These functions can be of different types and can be implemented in several programming languages.
(Refer to documentation for more details.
User-Defined Functions
)
PostgreSQL functions can be invoked in many ways. If you want to invoke a function as you would call a stored procedure in other RDBMS (typically a function with side-effects but whose result you don't care for example because it returns void), one option would be to use
PL/pgSQL Language
for your procedure and the
PERFORM
command. Example:
PERFORM theNameOfTheFunction(arg1, arg2);
Note that invoking instead:
SELECT theNameOfTheFunction(arg1, arg2);
would produce a result even if the function returns void (this result would be one row containing a void value).
PERFORM
could thus be used to discard this unuseful result.
The main limitations on Pg's stored functions - as compared to true stored procedures - are:
inability to return multiple result sets
no support for autonomous transactions (
BEGIN
,
COMMIT
and
ROLLBACK
within a function)
no support for the SQL-standard
CALL
syntax, though the ODBC and JDBC drivers will translate calls for you.
Why don't BEGIN, ROLLBACK and COMMIT work in stored procedures/functions?
PostgreSQL doesn't support autonomous transactions in its stored functions. Like all PostgreSQL queries, stored functions always run in a transaction and cannot operate outside a transaction.
If you need a stored procedure to manage transactions, you can look into the dblink interface or do the work from a client-side script instead. In some cases you can do what you need to using
exception blocks in PL/PgSQL
, because each BEGIN/EXCEPTION/END block creates a subtransaction.
Why is "SELECT count(*) FROM bigtable;" slow?
In 9.2 and above it generally isn't thanks to
Index-only scans
.
For more information on older versions, see
Slow Counting
.
Why is my query much slower when run as a prepared query?
In PostgreSQL 9.2 and above this issue is rare because PostgreSQL can decide to use a generic or value-optimised plan on a per-execution basis. The planner might still make the wrong choice, so the following remains somewhat relevant:
When PostgreSQL has the full query with all parameters known by planning time, it can use statistics in the table to find out if the values used in the query are very common or very uncommon in a column. This lets it change the way it fetches the data to be more efficient, as it knows to expect lots or very few results from a certain part of the query. For example, it might choose an sequential scan instead of doing an index scan if you search for 'active=y' and it knows that 99% of the records in the table have 'active=y', because in this case a sequential scan will be much faster.
In a prepared query, PostgreSQL doesn't have the value of all parameters when it's creating the plan. It has to try to pick a "safe" plan that should work fairly well no matter what value you supply as the parameter when you execute the prepared query. Unfortunately, this plan might not be very appropriate if the value you supply is vastly more common, or vastly less common, than is average for some randomly selected values in the table.
If you suspect this issue is affecting you, start by using the
EXPLAIN
command to compare the slow and fast queries. Look at the output of
EXPLAIN SELECT query...
and compare it to the result of
PREPARE query... ; EXPLAIN EXECUTE query...
to see if the plans are notably different.
EXPLAIN ANALYZE
may give you more information, such as row count estimates and counts.
Usually people having this problem are trying to use prepared queries as a security measure to prevent SQL injection, rather than as a performance tuning option for expensive-to-plan queries frequently executed with a variety of different parameters. Those people should consider using client-side prepared statements if their client interface (eg PgJDBC) supports it. The PostgreSQL protocol supports parameterised queries without server-side persistent prepared statements and most client drivers support using that via their client side prepared statement interfaces.
At present, PostgreSQL does not offer a way to request re-planning of a prepared statement using a particular set of parameter values; however, 9.2 and above may do so automatically where statistics indicate that it is desirable.
See
Using_EXPLAIN
. If you're going to ask for help on the mailing lists, please read the
Guide to reporting problems
.
Why is my query much slower when run in a function than standalone?
See
FAQ#Why is my query much slower when run as a prepared query?
. Queries in PL/PgSQL functions are prepared and cached, so they execute in much the same way as if you'd
PREPARE
d then
EXECUTE
d the query yourself.
If you're having really severe issues with this that improving the table statistics or adjusting your query don't help with, you can work around it by forcing PL/PgSQL to re-prepare your query at every execution. To do this, use the
EXECUTE ... USING
statement in PL/PgSQL to supply your query as a textual string. Alternately, the
quote_literal or quote_nullable
functions may be used to escape parameters substituted into query text.
Why do my strings sort incorrectly?
First, make sure you are using the locale you want to be using.  Use
SHOW lc_collate
to show the database-wide locale in effect.  If you are using per-column collations, check those.  If everything is how you want it, then read on.
PostgreSQL uses the C library's locale facilities for sorting strings.  So if the sort order of the strings is not what you expect, the issue is likely in the C library.  You can verify the C library's idea of sorting using the
sort
utility on a text file, e.g.,
LC_COLLATE=xx_YY.utf8 sort testfile.txt
If this results in the same order that PostgreSQL gives you, then the problem is outside of PostgreSQL.
PostgreSQL deviates from the libc behavior in so far as it breaks ties by sorting strings in byte order.  This should rarely make a
difference in practice, and is usually not the source of the problem when users complain about the sort order, but it could affect cases where, for example, combining and precombined Unicode characters are mixed.
If the problem is in the C library, you will have to take it up with your operating system maintainers.  Note, however, that while actual bugs in locale definitions of C libraries have been known to exist, it is more likely that the C library is correct, where "correct" means it follows some recognized international or national standard.  Possibly, you are expecting one of multiple equally valid interpretations of a language's sorting rules.
Common complaint patterns include:
Spaces and special characters: The sorting algorithm normally works in multiple passes.  First, all the letters are compared, ignoring spaces and punctuation.  Then, spaces and punctuation are compared to break ties.  (This is a simplification of what actually happens.)  It's not possible to change this without changing the locale definitions themselves (and even then it's difficult).  You might want to restructure your data slightly to avoid this problem.  For example, if you are sorting a name field, you could split the field into first and last name fields, avoiding the space in between.
Upper/lower case: Locales other than the C locale generally sort upper and lower case letters together.  So the order will be something like a A b B c C ... instead of the A B C ... a b c ... that a sort based on ASCII byte values will give.  That is correct.
German locale: sort order of ä as a or ae.  Both of these are valid (see
http://de.wikipedia.org/wiki/Alphabetische_Sortierung
), but most C libraries only provide the first one.  Fixing this would require creating a custom locale.  This is possible, but will take some work.
It is not in ASCII/byte order.  No, it's not, it's not supposed to be.  ASCII is an encoding, not a sort order.  If you want this, you can use the C locale, but then you use the ability to non-ASCII characters.
That said, if you are on Mac OS X or a BSD-family operating system, and you are using UTF-8, then give up.  The locale definitions on
those operating systems are broken.
Why doesn't PostgreSQL report a column not found error when using the wrong name in a subquery?
WITH tblA (id, foo_col) AS ( VALUES (1, 'A'), (2, 'B') ),
tblB (bar_col)     AS ( VALUES ('B'),    ('C') )
SELECT id
FROM tblA
WHERE foo_col IN (SELECT foo_col FROM tblB);
In the above query you will select both rows from
tblA
even though you are expecting only the row with id = 2 to be selected.  When you  finally figure out that there is no
foo_col
in
tblB
you will complain that PostgreSQL should realize that fact and complain.  However, per the SQL standard - and for good usability reasons - the reference to
foo_col
within the sub-select is found in the "outer reference" scope where
tblA
exists and which indeed has a
foo_col
column.  Since the expression
foo_col = foo_col
is always going to evaluate to true the where clause itself will always return true -
as long as
the sub-query (in this case
tblB
) returns at least one row (i.e.,
tblB WHERE false
will produce an empty result).
Specifically, the above query contains a correlated sub-query (
wikipedia
).  What that means is that logically the sub-select is evaluated once for each source row and its execution is paramertized during planning and then, during execution, the specific row values from the parent/outer query are injected.  Usage of correlated sub-queries in a sane and intentional way is outside the scope of this FAQ entry.
Aside from readability concerns many people will choose to append the table name to all column references used within a sub-query in order to avoid this error.  Specifying
tblB.foo_col
in the query will provoke the expected error.
As an aside, most reported queries of this form are malformed semi-join queries (i.e., they use IN instead of EXISTS).  Writing a proper semi-join query moves the column references to a where clause where usage of table references are more natural.
WITH tblA (id, foo_col) AS ( VALUES (1, 'A'), (2, 'B') ),
tblB (bar_col)     AS ( VALUES ('B'),    ('C') )
SELECT id
FROM tblA
WHERE EXISTS (SELECT 1
FROM tblB
WHERE tblB.bar_col = tblA.foo_col);
Discussing the merits of EXISTS vs IN is also outside the scope of this FAQ entry.
How do I prevent regular users from seeing my trade secrets?
You don't.  The system catalog does not take part in the grant/revoke based privileges system; any user with a login to a database can view the contents of the system catalog.
PostgreSQL stores all permanently created objects within system catalog tables, accessible via the pg_catalog schema.
All users, once logged into a database, can view the contents of nearly all tables (either directly or via views) within pg_catalog.  Of particular note are pg_proc (prosrc), and pg_views (definition), and pg_description (description).  The first two containing most of the stored business logic of the system while the later is a place where one can supply arbitrary metadata related to any objects.
You can get some level of secrecy by relying on C-language functions and procedures since only the DBA for the system is capable of viewing the source code for them.  You could also leverage foreign data wrappers or dblink.
Data Modelling Questions
How do I encrypt my data?
First, see
Bruce Momjian's presentation
on the general subject of data protection.  Also see
[GENERAL] Re: Two-way encryption
as a starting point.  Consider whether you need something like
automatically-encrypted types
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
