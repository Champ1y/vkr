---
title: "Warm Standby - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Warm_Standby.html"
source_url: "https://wiki.postgresql.org/wiki/Warm_Standby"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Warm Standby - PostgreSQL wiki

Warm Standby - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Warm Standby
Jump to navigation
Jump to search
There are a couple available Projects available to help you setup a warm standby system:
Use the walmgr.py portion of Skype's
SkyTools
package which will handle PITR backups from a primary to a single slave
Utilize Command Prompt's
PITR tools
to set everything up
But to actually get a warm standby up manually is actually a pretty simple process.  The following are notes only and intended to help your understanding. If you want to get this working correctly then please follow the manual, which is comprehensive and accurately maintained.
Warm Standby Manual
Pre-process recommendations
Use
pg_standby
for your restore_command in the recovery.conf file on the standby.  pg_standby is included in PostgreSQL 8.3, and you can copy the source from there to compile it for 8.2 yourself.  It isn't compatible with 8.1.
Set up your standby host's environment and directory structure exactly the same as your primary.  Otherwise you'll need to spend time changing any symlinks you've created on the primary for xlogs, tablespaces, or whatnot which is really just opportunity for error.
Pre-configure both the postgresql.conf and recovery.conf files for your standby.  I usually keep all of my different config files for all of my different servers in a single, version-controlled directory that I can then check out and symlink to.  Again, consistent environment & directory setups make symlinks your best friend.
Use ssh keys for simply, and safely, transferring files between hosts.
Follow all of the advice in the manual with respect to handling errors.
Outline of steps to get warm standby working
Make sure archive_mode is on in the master's postgresql.conf.
Set archive_command in the master's postgresql.conf.  rysnc is a popular choice or you can just use one of the examples from the docs.  I use:
rsync -a %p postgres@standbyhost:/path/to/wal_archive/%f
You must use a command here that does atomic copies, meaning that the file will never appear under the destination filename until it has been completely copied over.  This keeps the standby server from trying to read a partial file.  rsync is known to work.  A notable command that isn't atomic is scp.  If you want to use scp for this purpose, you will need to transfer files into another directory on the secondary, then move them to where the restore command looks for them after the transfer is complete.
If you're using pg_standby, it will refuse to apply files unless they are the right length, which lowers the risk of non-atomic copies being applied.  On Windows it even sleeps a bit after that to give time for things to settle. Performing the copy non-atomically is still a bad idea you should avoid.
Reload the master's config -- either: SELECT pg_reload_conf(); from psql or: pg_ctl reload -D data_dir/ . If you had to set archive_mode on, you'll have to restart your postgres server: pg_ctl restart -D data_dir/ .
Verify that the WALs are being shipped to their destination.
In psql, SELECT pg_start_backup('some_label');
Run your base backup.  Again, rsync is good for this with something as simple as:
rsync -a --progress /path/to/data_dir/* postgres@standbyhost:/path/to/data_dir/
I'd suggest running this in a screen term window, the --progress flag will let you watch to see how far along the rsync is. The -a flag will preserve symlinks as well as all file permissions & ownership.
In psql, SELECT pg_stop_backup();
This drops a file to be archived that will have the same name as the first WAL shipped after the call to pg_start_backup() with a .backup suffix.  Inside will be the start & stop WAL records defining the range of WAL files needed to be replayed before you can consider bringing the standby out of recovery.
Drop in, or symlink, your recovery.conf file in the standby's data_dir.
The restore command should use pg_standby (its help/README are simple and to the point).  I'd recommend redirecting all output from pg_standby to a log file that you can then watch to verify that everything is working correctly once you've started things.
Drop in, or symlink, your standby's postgresql.conf file.
If you don't symlink your pg_xlog directory to write WALs to a separate drive, you can safely delete everything under data_dir/pg_xlog on the standby host.
Start the standby db server with a normal: pg_ctl start -D /path/to/data_dir/
run a: tail -f on your standby log and watch to make sure that it's replaying logs.  If everything's cool you'll see some info on each WAL file, in order, that the standby looks for along with 'success' messages.  If it can't find the files for some reason, you'll see repeated messages like: 'WAL file not present yet.  Checking for trigger file...' (assuming you set up pg_standby to look for a trigger file in your recovery_command).
Execute this entire process at least a couple times, bringing up the standby into normal operations mode once it's played through all of the necessary WAL files (as noted in the .backup file) so that you can connect to it and verify that everything looks good, before doing all of this and leaving it running indefinitely.  Once you do it a couple times, it becomes dirt simple.
Adjusting frequency of WAL updates in 8.1
Often people want to know that their secondary is never more than some amount behind the primary.  The archive_timeout feature introduced into 8.2 allows doing that.  If you're using WAL replication with 8.1, you can force 16MB worth of WAL activity that doesn't leave any changes behind with a hack like this:
create table xlog_switch as
select '0123456789ABCDE' from generate_series(1,1000000);
drop table xlog_switch;
If you put that into cron etc. to run via psql and you can make the window for log shipping as fine as you'd like even with no activity.
If you do it too often you're increasing the odds it will interfere with real transactions though and it will use up more disk space; every couple of minutes is probably as often as you'd want to do this.  Using archive_timeout doesn't have this issue, the manual suggests it can be set to only a few seconds if necessary.
Additional resources
pg_standby lag monitoring
Simple HA with PITR
PostgreSQL 8.3 Warm Stand-by Replication
:  tutorial with Ubuntu specifics
Using pg_standby for high availability of Postgresql
:  tutorial that covers Debian, using 8.3 pg_standby on 8.2
Source material:
warm standby examples
Creating an 8.2 warm-standby demo system
PITR Base Backup on an idle 8.1 server
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
