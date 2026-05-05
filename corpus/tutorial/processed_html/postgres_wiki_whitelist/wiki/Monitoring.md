---
title: "Monitoring - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Monitoring.html"
source_url: "https://wiki.postgresql.org/wiki/Monitoring"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Monitoring - PostgreSQL wiki

Monitoring - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Monitoring
Jump to navigation
Jump to search
PostgreSQL builtin & contrib
Statistics collector
PostgreSQL collects lots of data on its own and offers it via the
pg_stat(io)_
system views
Official documentation on the
Statistics Collector
Interpreting pg_stat Views
contrib extensions
The following extensions offer access to Postgres internals which may be of interest or collect additional information. Most of them are shipped with Postgres (the
-contrib
packages may need to be installed) and can be activated via the
extension interface
.
pg_stat_statements
pg_stat_statements
tracks all queries that are executed on the server and records average runtime per query "class" among other parameters.
pg_stat_plans
pg_stat_plans
extends on pg_stat_statements and records query plans for all executed quries. This is very helpful when you're experiencing performance regressions due to inefficient query plans due to changed parameters or table sizes.
pgstattuple
pgstattuple
can generate statistics for tables and indexes, showing how much space in each table & index is consumed by live tuples, deleted tuples as well as how much unused space is available in each relation.
pg_buffercache
pg_buffercache
gives you introspection into Postgres'
shared buffers
, showing how many pages of which relations are currently held in the cache.
External projects
CLI tools
pg_view
pg_view
is a Python-based tool to quickly get information about running databases and resources used by them as well as correlate running queries and why they might be slow.
pg_activity
pg_activity
is a htop like application for PostgreSQL server activity monitoring, written in Python.
pgmetrics
pgmetrics
collects a lot of information and statistics from a running PostgreSQL server and displays it in easy-to-read text format or export it as JSON for scripting.
pgstats
pgstats
is a command line tool written in C which can sample various PostgreSQL informations. It also provides a tool to generate CSV files to graph the pgstats metrics.
pgcenter
pgcenter
is an admin tool for working with PostgreSQL stats, written in Golang. It provides top like viewer with a few admin functions, tool for recording stats into files and building reports.
Checkers
check_pgactivity
check_pgactivity
is designed to monitor PostgreSQL clusters from any Nagios like software. It offers many options to measure and monitor useful performance metrics.
check_postgres
check_postgres
is a command line tool which is designed to be run from software like Icinga, MRTG or as a standalone tool. It can monitor many aspects of the database and trigger warnings when thresholds are violated.
Interfaces & collectors
These tools either offer an interface to PostgreSQL monitoring-relevant data or can aggregate and prepare them for other systems.
pgsnmpd
pgsnmpd
can run as a standalone SNMP server and implements the
RFC 1697 MIB
which is generic RDBMS
MIB
This is useful for network management systems which are limited to SNMP protocol.
pganalyze/collector
pganalyze/collector
is a tool which collects
pg_stat_plans
query information as well as various performance-relevant database parameters and converts them into a JSON structure for easy ingestion in other systems.
pgexporter
pgexporter
is Prometheus exporter for PostgreSQL server metrics.
prometheus/postgres_exporter
prometheus/postgres_exporter
is Prometheus exporter for PostgreSQL server metrics.
weaponry/pgSCV
weaponry/pgSCV
is a multi-purpose monitoring agent and Prometheus-compatible exporter for PostgreSQL, Pgbouncer, etc.
Generic monitoring solutions with plugins
Cacti
There has been work done on building a Postgres template for
Cacti
, Details can be found at the
Cacti
page.
Circonus
Circonus
is a general purpose monitoring, analytic and alerting saas that has predefined queries for postgres to monitor some of the common metrics and checks like connections, transactions, WALs, vacuum and table stats. More information can be found
here
ClusterControl by Severalnines
ClusterControl
is an all-inclusive open source database management system that allows you to deploy, monitor, manage and scale your database environments. ClusterControl provides the basic functionality you need to get PostgreSQL up-and-running using the deployment wizard. It offers Advanced Performance Monitoring - ClusterControl monitors queries and detects anomalies with built-in alerts.  Deployment and monitoring are free, with management features as part of a paid version.
Datadog
Datadog
is a proprietary saas that collects postgres metrics on connections, transactions, row crud operations, locks, temp files, bgwriter, index usage, replication status, memory, disk, cpu and lets you visualize and alert on those metrics alongside your other system and application metrics.
Foglight for PostgreSQL
Foglight for PostgreSQL
offers a comprehensive monitoring solution that emphasizes detecting, diagnosing, and resolving issues. The product offers real-time monitoring and alerting through dashboards, rules, and reports from server-level metrics to individual query performance. Monitoring is supported from PostgreSQL version 9.1 for all platforms and includes drop-in replacements such as Aurora for PostgreSQL.
The solution is part of the industry-leading database monitoring platform
Foglight
from
Quest Software
.
Munin
PostgreSQL Plugins developed in Perl are included in the Core
Munin
Distribution. The following plugins are included by default:
postgres_bgwriter, postgres_locks_, postgres_tuples_, postgres_cache_, postgres_querylength_, postgres_users, postgres_checkpoints, postgres_scans_, postgres_xlog, postgres_connections_, postgres_size_, postgres_connections_db, postgres_transactions_
PyMunin
includes a Multigraph Munin Plugin written in Python that implements the following graphs:
pg_connections, pg_diskspace, pg_blockreads, pg_xact, pg_tup_read, pg_tup_write, pg_blockreads_detail, pg_xact_commit_detail, pg_xact_rollback_detail, pg_tup_return_detail, pg_tup_fetch_detail, pg_tup_delete_detail, pg_tup_update_detail, pg_tup_insert_detail
NewRelic
NewRelic
is a proprietary SaaS application monitoring solution which offers a
PostgreSQL plugin
maintained by EnterpriseDB.
Okmeter
Okmeter.io
is a proprietary SaaS that collects a whole lot of PostgreSQL status and operational data:  over 50 types of metrics on connections, transactions, table CRUD operations, locks, bgwriter, index usage and ops, replication, autovacuum. Also, query timings, disk and CPU usage by queries from pg_stat_statements, and system metrics — CPU, memory, fd and disk usage per process, socket connections per port and tcp status.  Collecting the data requires minimal to no configuration, there's pre-built
chart dashboards
, detailed query reports and pre-set alerts, that will notify you if something's wrong with you DB.
More information here
and
detailed info of what's collected - here.
Sematext
Sematext Cloud
is a monitoring SaaS that collects PostgreSQL metrics such as connections, transactions, row CRUD and index statistics, WAL archiver, brwriter and more. Complete list of metrics is
here
. Metrics can be correlated with data from logs (e.g. statement time), via the
Sematext PostgreSQL Logs integration
. An on-permises variant of Sematext Cloud is available as
Sematext Enterprise
.
Zabbix
pg_monz
is a
Zabbix
monitoring template for PostgreSQL.
libzbxpgsql
is a
Zabbix
monitoring template and native agent module for PostgreSQL.
Postgres-centric monitoring solutions
EnterpriseDB Postgres Enterprise Manager
Postgres Enterprise Manager
monitors, alerts, manages and tunes local and remote large scale Postgres deployments from a single graphical console. Out of the box features include: server auto-discovery, point and click management of database objects, 225+ pre-configured database alerts by SMTP/SNMP, custom alerts, global At-a-Glance monitoring dashboards, Performance monitoring dashboards, custom dashboards, an Audit Manager, Postgres Expert best practice configuration recommendations, a Log Manager, a Log Analyzer Expert, a SQL Profiler, and Index Advisor.
pganalyze
pganalyze
is a proprietary SaaS offering which focuses on performance monitoring and automated tuning suggestions.
pgwatch
pgwatch
is an open-source, scalable, flexible, and easy to install PostgreSQL-specific monitoring solution that offers a comprehensive view of database performance and health — without requiring extensions or superuser privileges. It provides a user-friendly interface through Grafana dashboards.
pg_statsinfo & pg_stats_reporter
pg_statsinfo
is a Postgres extension that collects lots of performance-relevant information inside the Postgres server which then can be aggregated by pg_stats_reporter instances which provide a web interface to the collected data. Both are FOSS software maintained by NTT.
PGObserver
PGObserver
is a Python & Java-based Postgres monitoring solution developed by Zalando. It was developed with a focus on stored procedure performance but extended well beyond that.
pgCluu
pgCluu
is a Perl-based monitoring solution which uses psql and
sar
to collect information about Postgres servers and render comprehensive performance stats.
PoWA
PoWA
is a PostgreSQL Workload Analyzer that gathers performance stats and provides real-time charts and graphs to help monitor and tune your PostgreSQL servers. It relies on extensions such as pg_stat_statements, pg_qualstats, pg_stat_kcache, pg_track_settings and HypoPG, and can help you optimize you database easily.  It's entirely open-source and free.
An online demo is available at
demo-powa.anayrat.info
.  Just click "login" to start using it.
OPM: Open PostgreSQL Monitoring
Open PostgreSQL Monitoring (OPM)
is a free software suite designed to help you manage your PostgreSQL servers. It's a flexible tool that will follow the activity of each instance. It can gather stats, display dashboards and send warnings when something goes wrong. The long-term goal of the project is to provide similar features to those of Oracle Grid Control or SQL Server Management Studio.
PASH-Viewer: PostgreSQL Active Session History Viewer
PASH-Viewer
is a free open-source software which provides graphical view of active session history and help you to answer questions like "What wait events were taking most time?", "Which sessions were taking most time?", "Which queries were taking most time and what were they doing?". It also supports Active Session History extension by pgsentinel.
Datasentinel
Datasentinel
is a proprietary monitoring and troubleshooting solution (SaaS or On-Premises ) helping you to quickly identify slowdowns thanks to its many features (sessions workload, complete activity statistics of sqls, databases, instances, and much more...)
temBoard
temBoard
is a free open source remote control and monitoring system. It uses an agent installed on the database machine and a PostgreSQL database as metadata repository.
Awide
Awide
is an enterprise-class proprietary solution that simplifies PostgreSQL clusters administration, monitoring, and troubleshooting. Available as SaaS and private cloud offerings and on-prem installation. Features include: ability to manage all enterprise PostgreSQL clusters in a single web interface, RDS databases management, configuration management and automation tuning, DB schema audits, live activities management including sessions and locks, query profiling, full monitoring solution including alters and integration with communication channels, and others.
Redgate Monitor
Redgate Monitor
is a proprietary monitoring solution from Redgate Software. It provides detailed database monitoring for PostgreSQL and SQL Server estates. Works with on-prem, DBaaS hosting, and a hybrid environment. It has a one screen, estate-wide overview to easily identify current or looming issues, query monitoring and recommendations, proactive alerts, database health metrics, advanced integration API, and more.
pg_statviz
pg_statviz
is a minimalist extension and utility pair for time series analysis and visualization of PostgreSQL internal statistics. Created for capturing PostgreSQL's cumulative and dynamic statistics,
pg_statviz
enables deeper time series analysis than the standard PostgreSQL statistics views. The included utility generates visualizations for selected time ranges from the stored statistic snapshots, helping users track PostgreSQL performance over time and potentially aiding in performance tuning and troubleshooting.
Validation & Data Monitoring
pg_isok
pg_isok
, an extension for monitoring and validating data using SQL queries.  Queries find problems.  Isok builds on this and tracks
changes
in problematic data, changes that might or might not indicate a new problem.  When configured to accept some questionable rows but not others of the same kind, Isok acts like a “soft trigger”, with scheduling and note-taking features to support the management of problem resolution.
Useful for "zero code required" batch-based data validation.  Most useful when review is required to determine whether a questionable data pattern should be allowed to remain in a database.
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
