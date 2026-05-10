---
title: "Performance Analysis Tools - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Performance_Analysis_Tools.html"
source_url: "https://wiki.postgresql.org/wiki/Performance_Analysis_Tools"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# Performance Analysis Tools - PostgreSQL wiki

Performance Analysis Tools - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Performance Analysis Tools
Jump to navigation
Jump to search
Performance Analysis Tools
This page is focused on tools for collecting data
outside
of PostgreSQL, in order to learn more about the system as a whole, about PostgreSQL's use of system resources, about things that may be bottlenecks for PostgreSQL's performance, etc.
Most of the time, the tools PostgreSQL provides internally will be more than adequate for your needs. The most important tool in your toolbox is the SQL
EXPLAIN
command and its
EXPLAIN ANALYZE
alternative. The
pg_catalog.pg_stat_activity
and
pg_catalog.pg_locks
views are also vital.
You can find a lot of advice about tuning PostgreSQL and the system in the
Performance
and categories of the wiki, and in
the PostgreSQL manual
. If you're at a loss, see
SlowQueryQuestions
.
System level tools for I/O, CPU and memory usage investigation
Tools like `ps' with the `wchan' format specifier, `vmstat', `top', `iotop', `blktrace' + `blkparse', `btrace', `sar', alt-sysrq-t, etc can help you learn much more about what your system is doing and where things are being delayed.
On supported systems (currently Solaris and FreeBSD), `dtrace' is also a powerful tool. PostgreSQL has DTrace hooks to allow you to investigate its internal workings and performance as well as that of the operating system it is running on.
Windows users will want to look into
Process Monitor
,
Process Explorer
, and
FileMon
from the
SysInternals
suite.
Unix/Linux tools
ps
The "wchan" option is really useful for seeing what a process that's in 'D' state (uninterruptable sleep in kernel system call) is actually doing. eg:
ps -e -o pid,ppid,wchan:60,cmd | grep post
You'll need to go digging in the kernel sources, use Google, or nut it out to figure what the value shown in the
wchan
field means.
vmstat
vmstat
can give you useful overview information about CPU, disk and memory activity at a system wide level. It's most useful when updating continuously, eg:
vmstat 1
or
vmstat 60
(the number is in seconds).
Output looks like:
$ vmstat 1
procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu----
r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa
0  0   4144 242088 707752 2307192    0    0     0    26   71   73  2  1 97  1
0  0   4144 242080 707752 2307220    0    0     0     0  944 1917  2  1 97  0
0  0   4144 241956 707752 2307220    0    0     0    64  772 1579  1  1 98  0
top
Like vmstat, gives you some system overview info, though isn't as useful for disk information. Quite configurable.
Don't be fooled by the "used" and "free" memory values. The
real
memory in use is actually (roughly) the value in "used" minus the value in "buffers", since "buffers" includes the kernel's disk cache. The kernel will use most of the free memory for disk cache, but will shrink that cache as required to fit other things into memory. After all, truly free memory is wasted memory that does you no good.
free
Shows free and used memory, system-wide.
$ free -m
total       used       free     shared    buffers     cached
Mem:          3960       3726        234          0        721       2252
-/+ buffers/cache:        752       3208
Swap:         2070          4       2066
The "free" value beside "-/+ buffers/cache" is the one you should generally consider the "real" amount of free memory in the system. The "-m" flag asks for values in megabytes.
sar
Process accounting. See the man page.
gdb
Why is a debugger listed in performance analysis tools?
Because sometimes, attaching a debugger to a backend, interrupting the backend periodically to get a backtrace, and then trying to figure out what on earth it's up to is a helpful way to track down an issue.
See
Generating a stack trace of a PostgreSQL_backend
Wireshark, tshark, and tcpdump
These tools are for monitoring and analysis of traffic on a network interface. If you can't figure out what's keeping your network interface pegged, they might help you figure out what data is being transmitted/received.
pktstat
A top-like utility for network interfaces. Doesn't, alas, show process IDs or names, but you can figure those out from source and destination port information. Handy for tracking down a backend that's flooding the interface with traffic.
Linux-only tools
atop
Atop
is an ASCII full-screen performance monitor for Linux that is capable of reporting the activity of all processes (even if processes have finished during the interval), daily logging of system and process activity for long-term analysis, highlighting overloaded system resources by using colors, etc. At regular intervals, it shows system-level activity related to the CPU, memory, swap, disks (including LVM) and network layers, and for every process (and thread) it shows e.g. the CPU utilization, memory growth, disk utilization, priority, username, state, and exit code.
iostat
Provides summary information about I/O activity and load on block devices in the system. Doesn't provide information about what processes are responsible for the load, but produces short and easily read output in real time. Like vmstat, most usefully used in continuous mode, eg "iostat 1".
See the man page for details.
blktrace, blkparse and btrace
These are tools to get very low level information about the activity on a given block device, what process(es) are causing that activity, and what they're doing. It produces a huge amount of information, but can be filtered somewhat. It takes a bit of thought to interpret, but can be great for those "what the hell is thrashing my disk" moments.
Because of the bgwriter and wal writer, it's not usually easy to see what PostgreSQL backends are keeping a disk busy with
writes
. It's still good for tracking down heavy read loads and figuring out what backend (and, thus, query - via the
pg_catalog.pg_stat_activity
) is responsible.
Output looks like this:
9,1    0      246    11.339004193  1383  U   N [postgres] 0
9,1    0      247    11.340029833  1383  A   R 118356256 + 96 <- (252,3) 34469792
9,1    0      248    11.340030339  1383  Q   R 118356256 + 96 [postgres]
9,1    0      249    11.340054022  1383  A   R 118356352 + 128 <- (252,3) 34469888
9,1    0      250    11.340054341  1383  Q   R 118356352 + 128 [postgres]
9,1    0      251    11.340062014  1383  A   R 118356480 + 32 <- (252,3) 34470016
9,1    0      252    11.340062367  1383  Q   R 118356480 + 32 [postgres]
... plus a handy summary at the end.
strace
strace
is a useful tool that can attach to a process and report all the system calls that process makes, including arguments to those system calls. It's great for figuring out what files a process opens, or if it's waiting for something, etc.
Useful interpretation requires some C programming knowledge and some idea about POSIX APIs.
(Note that other systems have similar tools with different names - for example, some BSDs have
truss
).
oprofile
Probably not useful for general users, but a handy tool if you have something within Pg or a library used by Pg that's running strangely slowly and you don't know why.
Profiling with OProfile
alt-sysrq-t
The "magic sysrq key". Mainly useful for tracking down processes mysteriously stuck in 'D' state in the kernel, ie hung in a system call, since it will output a stack trace of the kernel stack for all processes in the system. Mostly used when trying to figure out whether Pg is having problems due to a kernel bug, hardware issue, file system bug, etc.
Must be enabled with 'sysctl -w kernel.sysrq=1' before it can be used.
DTrace
See separate
DTrace
page.
Windows tools
dbForge Studio for PostgreSQL
Query Profiler functionality helps trace, recreate, and troubleshoot problems in PostgreSQL Server. With the tool, you can quickly and easily identify productivity bottlenecks and thus boost your database performance.
Process Monitor
Process Explorer
FileMon
PostgreSQL-centric performance tools
pgBadger
pgBadger
is a PostgreSQL log analyzer build for speed with fully detailed reports from your PostgreSQL log file.
PoWA
PoWA
(PostgreSQL Workload Analyzer) is a performance tool for PostgreSQL allowing to collect, aggregate and purge statistics on multiple PostgreSQL instances from various Stats Extensions (
pg_stat_statements
,
pg_qualstats
,
pg_stat_kcache
,
pg_wait_sampling
).
Web tools
Explain Depesz
Paste your explain analyze plan, and see the output. You can click on column headers to let it know which parameter is the most important for you – exclusive node time, inclusive node time, or rowcount mis-estimate.
https://explain.depesz.com/
Postgres EXPLAIN Visualiser (Pev)
Pev is designed to make Postgres query plans easier to grok. It displays a plan as a tree, with each node representing a step that takes in a row set and produces another.
http://tatiyants.com/pev/
Postgres EXPLAIN Visualiser 2 (Pev2)
This project is a rewrite of the excellent Postgres Explain Visualizer (pev).
The pev project was initially written in early 2016 but seems to be abandoned since then. There was no activity at all for more than 4 years and counting though there are several issues open and relevant pull requests pending.
The current project has several goals:
isolate the plan view component and its dependencies in order to use it in any web app with for example the ability to load a plan without requiring any copy-paste from the user,
make it work with recent version of JS frameworks,
upgrade Bootstrap to a more recent version,
use VueJS just for a matter of taste,
maintain the project to match upgrades in PostgreSQL.
https://explain.dalibo.com/
(GitHub project on
https://github.com/dalibo/pev2/
)
pgMustard
pgMustard visualises EXPLAIN output and gives tips on what to do to speed up your query.
https://www.pgmustard.com/
Explain-PostgreSQL
Analyzes EXPLAIN plan from PostgreSQL and related (Greenplum, Citus, TimescaleDB and Amazon RedShift).
Shows plan and node details and visualizations with piechart, flowchart and tilemap, also gives smart recommendations to improve query. Free for personal use.
https://explain-postgresql.com
Page originally by --
Ringerc
07:26, 26 November 2009 (UTC)
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
