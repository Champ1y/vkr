---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/timestamp.html"
source_url: "https://pgexercises.com/questions/date/timestamp.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a timestamp for 1 a.m. on the 31st of August 2012
Question
Produce a timestamp for 1 a.m. on the 31st of August 2012.
Schema reminder
▼
Expected Results
timestamp
2012-08-31 01:00:00
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select timestamp '2012-08-31 01:00:00';
Here's a pretty easy question to start off with!  SQL has a bunch of different date and time types, which you can peruse at your leisure over at the excellent
Postgres documentation
.  These basically allow you to store dates, times, or timestamps (date+time).
The approved answer is the best way to create a timestamp under normal circumstances.  You can also use casts to change a correctly formatted string into a timestamp, for example:
select '2012-08-31 01:00:00'::timestamp;
select cast('2012-08-31 01:00:00' as timestamp);
The former approach is a Postgres extension, while the latter is SQL-standard.  You'll note that in many of our earlier questions, we've used bare strings without specifying a data type.  This works because when Postgres is working with a value coming out of a timestamp column of a table (say), it knows to cast our strings to timestamps.
Timestamps can be stored with or without time zone information.  We've chosen not to here, but if you like you could format the timestamp like "2012-08-31 01:00:00 +00:00", assuming UTC.  Note that timestamp with time zone is a different type to timestamp - when you're declaring it, you should use
TIMESTAMP WITH TIME ZONE 2012-08-31 01:00:00 +00:00
.
Finally, have a bit of a play around with some of the different date/time serialisations described in the Postgres docs.  You'll find that Postgres is extremely flexible with the formats it accepts, although my recommendation to you would be to use the standard serialisation we've used here - you'll find it unambiguous and easy to port to other DBs.
/
/
Timestamp
Next Exercise
There's a bunch of ways to do this, but the easiest is probably to look at the
TIMESTAMP
keyword.
Keyboard shortcuts:
Alt-h
: Show/Hide Help menu
Alt-r
: Run query
Alt-x
: Run selected text as query
Alt-s
: Run query by cursor (delimited by whitespace/semi-colon)
Other hints:
You can double click on each of the panes of Expected Result/Your answer to quickly resize them.
If you have trouble remembering the database schema, you can leave this popup open while you work on your answer.
Don't forget to use the hint button if you're stuck!
