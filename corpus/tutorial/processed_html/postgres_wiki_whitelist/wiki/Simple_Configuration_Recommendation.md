---
title: "Simple Configuration Recommendation - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Simple_Configuration_Recommendation.html"
source_url: "https://wiki.postgresql.org/wiki/Simple_Configuration_Recommendation"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Simple Configuration Recommendation - PostgreSQL wiki

Simple Configuration Recommendation - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Simple Configuration Recommendation
Jump to navigation
Jump to search
PostgreSQL Configuration Recommendations
Administration of database environments requires resources from separate disciplines.  Database administrators (DBA) must work closely with the system and storage administrators.  PostgreSQL relies heavily on the host operating system (OS) for storage management.  It does not have the advanced and complicated features of Oracle for storage management.
These recommendations are to standardize and simplify PostgreSQL database configurations.
Software Location and Ownership
The common location for PostgreSQL software on Linux is /usr/local/pgsql with the executables, source, and data existing in various subdirectories.  However, PostgreSQL is open source software and whoever the distributor, packager, or supporter will have their
recommendations as to where to place the software and what account owns the software.
Prefer available packages for your operating system over compiling the server locally. The packages have been developed to integrate well into the operating system, neglecting their use means you have to re-do the work that went into creating the packages. (The recommendations here do not necessarily align with the packager's choice of options. When choosing which way to follow, stick with a consistent set.)
The owner and group of the software, database files, and server processes should be postgres:dba.  The UID and GID have to be worked out with system administration.
Create a base software destination directory:
/opt/postgres
Define the software installation using the first 2 digits of the software version (9.0 as the example):
/opt/postgres/9.0
Be advised upgrading with the third digit in the version number usually entails stopping the server, switching to the new software, and restarting the server.  However, upgrading the first or second digit requires an upgrade of all of the data files.  Keeping the software versions separate helps with upgrades.
Single Cluster and Database per Server
The following database objects are cluster wide within PostgreSQL, having only one database per cluster is preferable:
Configuration files
WAL (on-line and archived) files
Tablespaces
User accounts and roles
Server log file
An older style of database object separation was through the use of multiple databases.  An alternate and more manageable method to separate database objects within a single database server is through the use of schemas.
To separate PostgreSQL clusters within a server different data areas and IP port numbers need to be created.  However, the virtualization capabilities of the OSes like Solaris’s zones and FreeBSD jails or hypervisors like
Xen
and
KVM
make creation of multiple clusters within a single host unnecessary.  The recommendation is to have only one PostgreSQL cluster per virtualized host.
File System Layouts
To create the most flexible and manageable environment, separate the various database components into their own file systems.  Create the following file systems (mount points):
/pgarchive
DB Archive location containing the archive log files.
/pgbackup
DB Backup location containing the physical and logical backups.  For logical backups (pg_dump), use EXPORTS as a sub directory. For physical backups, use FULL{date}, convention for the sub directory.  However, physical backups could be handled with file system snapshots.  More on this later.
/pgcluster
PostgreSQL Cluster data directory (PGDATA environment variable).  This will contain all of the configuration files and directories of a PostgreSQL cluster.  Note: the on-line WAL files would be located in /pgcluster/pg_xlog.
/pglog
The location of the server log files.
/pgdata-system
The location of a database’s default tablespace.  This is to be used at the creation of the database.   The database catalog information will be stored.
/pgdata-temp
The location of the database’s default temporary tablespace.  This is needed for temporary sort information.  Note: The pgsql_tmp directory within the default tablespace will be used if a temporary tablespace is not defined.
/pgdata-
app_tblspc
Application tablespaces.  For every schema there should be a minimum of two tablespaces.  One for tables and one for indexes.
PostgreSQL does not have declarative size limitations for its tablespaces and database objects; the OS is expected to manage the size of used devices.  This is why it is recommended to create a separate mount point (file system) for every tablespace.  This adds a layer of complexity especially in organizations that segregate storage and OS management from database management.  However, that level of complexity is outweighed by the advantage of separation and segregation of database objects.
It is desirable for the file system growth and management to be in the form of distributed administration.  A DBA would be given a set of disk groups within a volume manager and then carve up the file systems accordingly.
ZFS
is an example of a file system that has delegated administration.
Server Configuration Information
Use "Continuous Archiving" for Point-In-Time Recovery (PITR).
archive_mode = on
archive_command = 'cp %p /pgarchive/%f'
wal_level = 'archive'
Setup a server log file rotation.  (7 days or 10MB, whichever comes first)
log_directory = '/pgcluster/log'
log_filename = 'postgresql-%Y%m%d_%H%M%S.log'
log_rotation_age = 7d
log_rotation_size = 10MB
log_truncate_on_rotation = off
log_line_prefix = '%t c%  '
Gather connection information in server log file.
log_connections = on
log_disconnections = on
Log DDL transactions.
log_statement = 'ddl'
Enable SSL traffic.
ssl = on
ssl_ciphers = 'ALL'
Either drop the default postgres database or deny remote connections to it.
Create a database to place application schemas within.  Drop the public schema.
Account Management
Avoid connecting to the database server as the database superuser, postgres.  Management processes, like backups, will most likely still use the postgres account; however users and applications should not.  Allow only local connections to the postgres database user.  Note: In version 9.1 using the authentication model within pg_hba.conf of local with auth-option peer is the most preferable.
Create individual accounts for all the users that will be connecting directly to the database.  DBAs will need superuser privileges, deployment representatives will need privileges to manipulate schema object definitions, developers will need select privileges on application objects to diagnose production issues.
Where possible use centralized enterprise accounts (i.e., LDAP) for user account authentication.
Create accounts to be synonymous with application schemas.  Avoid connecting to those schema accounts.  In fact where possible make the account NOLOGIN.
When users are deploying object definitions into the application schemas, they will need to have the appropriate privileges.  Granting those users the role of the application schema is sufficient to allow this activity.  Make sure that for any newly created object the ownership is set to the account that matches the schema.
To ease management of accounts, use roles for granting privileges to users versus direct grants.
Generally applications connect to the database using pooled (shared) accounts.  Make sure those accounts can only connect to the database from the defined application servers.  Users should not be allowed to log directly into the database using those pooled accounts.
Physical Database Backups
To perform on-line backups it is important that the database be in archive log mode.  Refer to the
Continuous Archiving and Point-In-Time Recovery
chapter in the PostgreSQL reference manual.
Using an advanced file system like ZFS that has snapshot/rollback capabilities has some significant advantages.  Placing the database in hot backup mode, snapshoting the file systems that make up the database storage, and taking the database out of backup mode is preferable to using tar or cpio to copy all of the data files to an alternate location during the backup process.
After the snapshots have been taken coping the data files to an alternate location for safe keeping is still an option; however, the database is only in hot backup mode for a short amount of time while the snapshot is taken.  For most recovery situations using the on-line backups (the snapshots) is used instead of "pulling from tape".
File system delegated administration is an advantage for management of the file system snapshots.  DBAs will have to coordinate with the system and storage administration to facilitate the best practices.
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
