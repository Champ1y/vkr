---
title: "Detailed installation guides - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Detailed_installation_guides.html"
source_url: "https://wiki.postgresql.org/wiki/Detailed_installation_guides"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Detailed installation guides - PostgreSQL wiki

Detailed installation guides - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Detailed installation guides
Jump to navigation
Jump to search
Any UNIX-Like Platform
Compile and Install from source code
Manual Setup at the Command Line
General Linux
Gentoo:
PostgreSQL Guide
PostgreSQL and SELinux
Installation of Postgres Plus Standard Server v8.3 Tutorial for Linux
Debian/Ubuntu Linux
Debian based installs have a somewhat unique design that allows multiple database clusters to be managed independently.  This allows running both multiple database instances as well as multiple versions more easily than other packaging schemes.
PostgreSQL provides debian packages:
see entry point at apt.postgresql.org
.
Note: if you do not wish, for example, PostgreSQL or Slony to start automatically when the software is upgraded, do the following:
echo 'if $1 in postgresql-9.3|slony1-2 then exit 101 else exit 0' > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d
Official Ubuntu Community Wiki
Debian PostgreSQL Wiki
.  As pointed out there, really detailed documentation is available on the server at
/usr/share/doc/postgresql-common/README.Debian.gz
; you should copy this file to another directory and run
gunzip README.Debian.gz
if you'd like a readable version.
Using PostgreSQL on Debian and Ubuntu
(2016)
Install Ubuntu 9.04 Server Edition, Rails, PHP, Passenger, PostgreSQL, and MySQL
- the "database" section here is a concise guide to the standard PostgreSQL installation work most systems need to password-protected remote access, and it also covers installing the server side tools for pgAdmin (2009-05-25)
Install PostgreSQL on Ubuntu 8.04
(2008-05-14)
Howto setup Database Server With postgresql and pgadmin3
(2008, has a nice intro to general postgresql.conf/pg_hba.conf info applicable to all distributions)
PostgreSQL Database Server Configuration in Debian
postgresql clustering and Debian
(2006)
Upgrading to PostgreSQL 8.3 in Debian from 7.4
RedHat/Fedora/CentOS
YUM Installation
PostgreSQL on RedHat Linux
FreeBSD
FreeBSD:
Upgrading PostgreSQL on FreeBSD
(2011-01-01)
FreeBSD:
Installing PostgreSQL on FreeBSD
(2010-01-11)
FreeBSD:
PostgreSQL Installation on FreeBSD
(2002-08-24)
FreeBSD:
PostgreSQL and Perl on FreeBSD
(2000-12-26)
MacOS
MacOs X:
Setup PostgreSQL development environment on MacOS
(2023) - Development tools via Homebrew / Compile from Source
MacOS X:
Postgres.app for macOS 10.12 or later
(2022) - conventional Mac-style drag-and-drop app installation
MacOS X:
Install PostgreSQL 9 on OS X
(2010-11-25) - Easy install using Homebrew package manager.
MacOS X:
Installing PostgreSQL on Mac OS X (an alternative guide using EnterpriseDB) by Jeremiah Peschka
(2010-02-15)
MacOS X:
PostgreSQL on Mac OS X 10.7 Server
Solaris
Solaris 10:
PostgreSQL 8.2.1 on Solaris 10 – Deployment Guidelines
by Chris Drawater (2007-01-15)
Solaris 10:
Related documents for J2EE, Tomcat, and Oracle migrations
by Chris Drawater (2007-01-15)
PostgreSQL 8.1 on Solaris 10 - Deployment Guidelines
(160KB - PDF)
Windows
Running & Installing PostgreSQL On Native Windows
Building_With_MinGW
Video explaining how to compile Postgres on Win64
Alternative to manual installation
Some users may prefer to skip manual installation by using a pre-integrated
PostgreSQL software appliance
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
