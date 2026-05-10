---
title: "Streaming Replication - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Streaming_Replication.html"
source_url: "https://wiki.postgresql.org/wiki/Streaming_Replication"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

# Streaming Replication - PostgreSQL wiki

Streaming Replication - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Streaming Replication
Jump to navigation
Jump to search
Streaming Replication
(SR) provides the capability to continuously ship and
apply the
WAL XLOG
records to some number of standby servers in order to keep them current.
This feature was added to PostgreSQL 9.0.  The discussion below is a developer oriented one that contains some out of date information, particularly for PostgreSQL 10 and later.  Users of this feature should refer to the current
PostgreSQL Streaming Replication Documentation
.
Developer and historical details on the project
SR was developed for inclusion in PostgreSQL 9.0 by NTT OSS Center. The lead developer is
Masao Fujii
.
Synchronous Log Shipping Replication Presentation
introduces the early design of the feature.
Usage
Users Overview
Log-shipping
XLOG records generated in the primary are periodically shipped to the standby via the network.
In the existing warm standby, only records in a filled file are shipped, what's referred to as file-based log-shipping.  In SR, XLOG records in partially-filled XLOG file are shipped too, implementing record-based log-shipping.  This means the window for data loss in SR is usually smaller than in warm standby, unless the warm standby was also configured for record-based shipping (which is complicated to setup).
The content of XLOG files written to the standby are exactly the same as those on the primary. XLOG files shipped can be used for a normal recovery and PITR.
Multiple standbys
More than one standby can establish a connection to the primary for SR. XLOG records are concurrently shipped to all these standbys. The delay/death of a standby does not harm log-shipping to other standbys.
The maximum number of standbys can be specified as a GUC variable.
Continuous recovery
The standby continuously replays XLOG records shipped without using pg_standby.
XLOG records shipped are replayed as soon as possible without waiting until XLOG file has been filled. The combination of
Hot Standby
and SR would make the latest data inserted into the primary visible in the standby almost immediately.
The standby periodically removes old XLOG files which are no longer needed for recovery, to prevent excessive disk usage.
Setup
The start of log-shipping does not interfere with any query processing on the primary.
The standby can be started in various conditions.
If there are XLOG files in archive directory and restore_command is supplied, at first those files are replayed. Then the standby requests XLOG records following the last applied one to the primary. This prevents XLOG files already present in the standby from being shipped again. Similarly, XLOG files in pg_xlog are also replayed before starting log-shipping.
If there is no XLOG files on the standby, the standby requests XLOG records following the starting XLOG location of recovery (the redo starting location).
Connection settings and authentication
A user can configure the same settings as a normal connection to a connection for SR (e.g., keepalive, pg_hba.conf).
Activation
The standby can keep waiting for activation as long as a user likes. This prevents the standby from being automatically brought up by failure of recovery or network outage.
Progress report
The primary and standby report the progress of log-shipping in PS display.
Graceful shutdown
When smart/fast shutdown is requested, the primary waits to exit until XLOG records have been sent to the standby, up to the shutdown checkpoint record.
Restrictions
Synchronous log-shipping
By default, SR supports operates in asynchronous manner, so the commit command might return a "success" to a client before the corresponding XLOG records are shipped to the standby. To enable synchronous replication, see
Synchronous Replication
Replication beyond timeline
A user has to get a fresh backup whenever making the old standby catch up.
Clustering
Postgres doesn't provide any clustering feature.
How to Use
NB: there is overlap between this section and
Binary Replication Tutorial
1.
Install postgres in the primary and standby server as usual.  This requires only
configure
,
make
and
make install
.
2.
Create the initial database cluster in the primary server as usual, using
initdb
.
3.
Create an user named replication with REPLICATION privileges.
$ CREATE ROLE replication WITH REPLICATION PASSWORD 'password' LOGIN;
4.
Set up connections and authentication on the primary so that the standby server can successfully connect to the
replication
pseudo-database on the primary.
$ $EDITOR postgresql.conf

listen_addresses = '192.168.0.10'
$ $EDITOR pg_hba.conf

# The standby server must connect with a user that has replication privileges.
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host  replication     replication     192.168.0.20/32         md5
5.
Set up the streaming replication related parameters on the primary server.
$ $EDITOR postgresql.conf

# To enable read-only queries on a standby server, wal_level must be set to
# "hot_standby". But you can choose "archive" if you never connect to the
# server in standby mode.
wal_level = hot_standby

# Set the maximum number of concurrent connections from the standby servers.
max_wal_senders = 5

# To prevent the primary server from removing the WAL segments required for
# the standby server before shipping them, set the minimum number of segments
# retained in the pg_xlog directory. At least wal_keep_segments should be
# larger than the number of segments generated between the beginning of
# online-backup and the startup of streaming replication. If you enable WAL
# archiving to an archive directory accessible from the standby, this may
# not be necessary.
wal_keep_segments = 32

# Enable WAL archiving on the primary to an archive directory accessible from
# the standby. If wal_keep_segments is a high enough number to retain the WAL
# segments required for the standby server, this is not necessary.
archive_mode    = on
archive_command = 'cp %p /path_to/archive/%f'
6.
Start postgres on the primary server.
7.
Make a base backup by copying the primary server's data directory to the standby server.
7.1.
Do it with pg_(start|stop)_backup and rsync on the primary
$ psql -c "SELECT pg_start_backup('label', true)"
$ rsync -ac ${PGDATA}/ standby:/srv/pgsql/standby/ --exclude postmaster.pid
$ psql -c "SELECT pg_stop_backup()"
7.2.
Do it with pg_basebackup on the standby
In version 9.1+, pg_basebackup can do the dirty work of fetching the entire data directory of your PostgreSQL installation from the primary and placing it onto the standby server.
The prerequisite is that you make sure the standby's data directory is empty.
Make sure to remove any tablespace directories as well. You can find those directories with:
$ psql -c '\db'
If you keep your postgresql.conf and other config files in PGDATA, you need a backup of postgresql.conf, to restore after pg_basebackup.
After you've cleared all the directories, you can use the following command to directly stream the data from the primary onto your standby server.
Run it as the database superuser, typically 'postgres', to make sure the permissions are preserved (use su, sudo or whatever other tool to make sure you're not root).
$ pg_basebackup -h 192.168.0.10 -D /srv/pgsql/standby -P -U replication --xlog-method=stream
In version 9.3+, you can also add the -R option so it creates a minimal recovery command file for step 9 below.
If you backed up postgresql.conf, now restore it.
8.
Set up replication-related parameters, connections and authentication in the standby server like the primary, so that the standby might work as a primary after failover.
9.
Enable read-only queries on the standby server. But if wal_level is
archive
on the primary, leave hot_standby unchanged (i.e., off).
$ $EDITOR postgresql.conf

hot_standby = on
10.
Create a recovery command file in the standby server; the following parameters are required for streaming replication.
$ $EDITOR recovery.conf
# Note that recovery.conf must be in the $PGDATA directory, even if the
# main postgresql.conf file is located elsewhere.

# Specifies whether to start the server as a standby. In streaming replication,
# this parameter must to be set to on.
standby_mode          = 'on'

# Specifies a connection string which is used for the standby server to connect
# with the primary.
primary_conninfo      = 'host=192.168.0.10 port=5432 user=replication password=password'

# Specifies a trigger file whose presence should cause streaming replication to
# end (i.e., failover).
trigger_file = '/path_to/trigger'

# Specifies a command to load archive segments from the WAL archive. If
# wal_keep_segments is a high enough number to retain the WAL segments
# required for the standby server, this may not be necessary. But
# a large workload can cause segments to be recycled before the standby
# is fully synchronized, requiring you to start again from a new base backup.
restore_command = 'cp /path_to/archive/%f "%p"'
11.
Start postgres in the standby server. It will start streaming replication.
12.
You can calculate the replication lag by comparing the current WAL write location on the primary with the last WAL location received/replayed by the standby. They can be retrieved using
pg_current_xlog_location
on the primary and the
pg_last_xlog_receive_location
/
pg_last_xlog_replay_location
on the standby, respectively.
$ psql -c "SELECT pg_current_xlog_location()" -h192.168.0.10 (primary host)
pg_current_xlog_location
--------------------------
0/2000000
(1 row)

$ psql -c "select pg_last_xlog_receive_location()" -h192.168.0.20 (standby host)
pg_last_xlog_receive_location
-------------------------------
0/2000000
(1 row)

$ psql -c "select pg_last_xlog_replay_location()" -h192.168.0.20 (standby host)
pg_last_xlog_replay_location
------------------------------
0/2000000
(1 row)
13.
You can also check the progress of streaming replication by using
ps
command.
# The displayed LSNs indicate the byte position that the standby server has
# written up to in the xlogs.
[primary] $ ps -ef | grep sender
postgres  6879  6831  0 10:31 ?        00:00:00 postgres: wal sender process postgres 127.0.0.1(44663) streaming 0/2000000

[standby] $ ps -ef | grep receiver
postgres  6878  6872  1 10:31 ?        00:00:01 postgres: wal receiver process   streaming 0/2000000
How to do failover
Create the trigger file in the standby after the primary fails.
How to stop the primary or the standby server
Shut down it as usual (
pg_ctl stop
).
How to restart streaming replication after failover
Repeat the operations from
6th
; making a fresh backup, some configurations and starting the original primary as the standby. The primary server doesn't need to be stopped during these operations.
How to restart streaming replication after the standby fails
Restart postgres in the standby server after eliminating the cause of failure.
How to disconnect the standby from the primary
Create the trigger file in the standby while the primary is running. Then the standby would be brought up.
How to re-synchronize the stand-alone standby after isolation
Shut down the standby as usual. And repeat the operations from
6th
.
If you have more than one standby, promoting one will break the other(s). Update their recovery.conf settings to point to the new master, set recovery_target_timeline to 'latest', scp/rsync the pg_xlog directory, and restart the standby.
Todo
v9.0
Moved to
PostgreSQL_9.0_Open_Items
Committed
Retrying from archive and some refactoring around Read/FetchRecord().
-
commit
SR wrongly treats the WAL-boundary.
-
commit
Adjust SR for some later changes about wal-skipping.
-
commit
VACUUM FULL unexpectedly writes an XLOG UNLOGGED record.
-
commit
Add a message type header.
-
commit
Documentation: Add a new "Replication" chapter.
-
commit
Failed assertion during recovery of partial WAL file.
-
commit
A PANIC error might occur in the standby because of a partially-filled archived WAL file.
-
commit
Improve the standby messages.
-
commit
pq_getbyte_if_available() is not working because the win32 socket emulation layer simply wasn't designed to deal with non-blocking sockets.
-
commit
Walsender might emit unfit messages.
-
commit
Streaming replication on win32, still broken.
-
commit
Create new section for recovery.conf.
-
commit
Assertion failure in walreceiver.
-
commit
Forbid a startup of walsender during recovery, and emit a suitable message? Or allow walsender to be started also during recovery?
-
commit
How do we clean down the archive without using pg_standby?
-
commit
File-based log shipping without pg_standby doesn't replay the WAL files in pg_xlog.
-
commit
v9.1
Synchronization capability
Introduce the replication mode which can control how long transaction commit waits for replication before the commit command returns a "success" to a client. The valid modes are
async
,
recv
and
fsync
.
async
doesn't make transaction commit wait for replication, i.e., asynchronous replication.
recv
or
fsync
makes transaction commit wait for XLOG to be received or fsynced by the standby, respectively.
(
apply
makes transaction commit wait for XLOG to be replayed by the standby. This mode will be supported in v9.2 or later)
The replication mode is specified in recovery.conf of the standby as well as other parameters for replication.
The startup process reads the replication mode from recovery.conf and shares it to walreceiver via new shared-memory variable.
Walreceiver also shares it to walsender by using the replication handshake message (existing protocol needs to be extended).
Based on the replication mode, walreceiver sends the reply meaning that replication is done up to the specified location to the primary.
In async, walreceiver doesn't need to send any reply other than end-of-replication message.
In recv or fsync, walreceiver sends the reply just after receiving or flushing XLOG, respectively.
New message type for the reply needs to be defined. The reply is sent as CopyData message.
Walreceiver writes all the outstanding XLOG to disk before shutting down.
Walsender receives the reply from the standby, updates the location of the last record replicated, and announces completion of replication.
New shared-memory variable to keep that location is required.
When processing the commit command, backend waits for XLOG to be replicated to only the standbys which are in the recv or fsync replication mode.
Also smart shutdown waits for XLOG of shutdown checkpoint to be replicated.
Required optimization
Walsender should send outstanding XLOG without waiting wal_sender_delay.
When processing the commit command, backend signals walsender to send outstanding XLOG immediately.
Backend should exit the wait loop as soon as the reply arrives at the primary.
When receiving the reply, walsender signals backends to get up from the sleep and determine whether to exit the wait loop by checking the location of the last XLOG replicated.
Only backends waiting for XLOG to be replicated up to the location contained in the reply are sent the signal.
Walsender waits for the signal from backends and the reply from the standby at the same time, by using select/poll.
Walsender reads XLOG from not only disk but also shared memory (wal buffers).
Walreceiver should flush XLOG file only when XLOG file is switched or the related page is flushed.
When startup process or bgwriter flushes the buffer page, it checks whether the related XLOG has already been flushed via shared memory (location of the last XLOG flushed).
It flushes the buffer page, if XLOG file has already been flushed.
It signals walreceiver to flush XLOG file immediately and waits for the flush to complete, if XLOG file has not been flushed yet.
While the standby is catching up with the primary, those servers should ignore the replication mode and perform asynchronous replication.
After those servers have almost gotten into synchronization, they perform replication based on the specified replication mode.
New replication states like 'catching-up', 'sync', etc need to be defined, and the state machine for them is required on both servers.
Current replication state can be monitored on both servers via SQL.
Required timeout
Add new parameter replication_timeout which is the maximum time to wait until XLOG is replicated to the standby. (does this match
http://www.postgresql.org/docs/current/interactive/runtime-config-replication.html
?)
Add new parameter (replication_timeout_action) to specify the reaction to replication_timeout.
Future release
Synchronization capability
Introduce the synchronization mode which can control how long transaction commit waits for replication before the commit command returns a "success" to a client. The valid modes are
async
,
recv
,
fsync
and
apply
.
async
doesn't make transaction commit wait for replication, i.e., asynchronous replication.
recv
,
fsync
and
apply
makes transaction commit wait for XLOG records to be received, fsynced and applied on the standby, respectively.
Change walsender to be able to read XLOG from not only the disk but also shared memory.
Add new parameter replication_timeout which is the maximum time to wait until XLOG records are replicated to the standby. (does this match
http://www.postgresql.org/docs/current/interactive/runtime-config-replication.html
?)
Add new parameter (replication_timeout_action) to specify the reaction to replication_timeout.
Monitoring
Provide the capability to check the progress and gap of streaming replication via one query. A collaboration of HS and SR is necessary to provide that capability on the standby side.
Provide the capability to check if the specified repliation is in progress via a query. Also more detailed status information might be necessary, e.g, the standby is catching up now, has already gotten into sync, and so on.
Change the stats collector to collect the statistics information about replication, e.g., average delay of replication time.
Develop the tool to calculate the latest XLOG position from XLOG files. This is necessary to check the gap of replication after the server fails.
Also develop the tool to extract the user-readable contents from XLOG files. This is necessary to see the contents of the gap, and manually restore them.
Easy to Use
Introduce the parameters like:
replication_halt_timeout - replication will halt if no data has been sent for this much time.
replication_halt_segments - replication will halt if number of WAL files in pg_xlog exceeds this threshold.
These parameters allow us to avoid disk overflow.
Add new feature which transfers also base backup via the direct connection between the primary and the standby.
Add new hooks like walsender_hook and walreceiver_hook to cooperate with the add-on program for compression like pglesslog.
Provide a graceful termination of replication via a query on the primary. On the standby, a trigger file mechanism already provides that capability.
Support replication beyond timeline. The timeline history files need to be shipped from the primary to the standby.
Robustness
Support keepalive in libpq. This is useful for a client and the standby to detect a failure of the primary immediately.
Miscellaneous
Standalone walreceiver tool, which connects to the primary, continuously receives and writes XLOG records, independently from postgres server.
Cascade streaming replication. Allow walsender to send XLOG to another standby during recovery.
WAL archiving during recovery.
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
