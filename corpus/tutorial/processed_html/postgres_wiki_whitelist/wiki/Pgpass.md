---
title: "Pgpass - PostgreSQL wiki"
language: "en"
corpus_type: "supplementary"
source_role: "external_troubleshooting_whitelist"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/postgres_wiki_whitelist/wiki/Pgpass.html"
source_url: "https://wiki.postgresql.org/wiki/Pgpass"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

# Pgpass - PostgreSQL wiki

Pgpass - PostgreSQL wiki
Want to edit, but don't see an edit button when logged in?  Click here.
Pgpass
Jump to navigation
Jump to search
Most access to the database, including the psql program, goes through the libpq library.  This library includes a feature where if you specify a file called
.pgpass
(or the file referenced by PGPASSFILE) you can put the password needed to connect as a user in there.  This allows automating routine administration tasks through mechanisms like cron.
The format of the .pgpass file is the following:
hostname:port:database:username:password
When the password contains a colon (:), it must be escaped by a backslash (\:).
the character '*' can match any value in any of the fields (except password)
n.b.: if the environment variable
PGPASSWORD
is set, then the ~/.pgpass file is not read
Example PGPASSFILE value for a path with spaces on Windows 7 64-bit:
set PGPASSFILE=C:\Program Files\someapp\pgpass.conf
Note that the environment variable value must not use " (double quotes).
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
