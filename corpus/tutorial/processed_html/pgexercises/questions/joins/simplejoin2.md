---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/simplejoin2.html"
source_url: "https://pgexercises.com/questions/joins/simplejoin2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Work out the start times of bookings for tennis courts
Question
How can you produce a list of the start times for bookings for tennis courts, for the date '2012-09-21'?  Return a list of start time and facility name pairings, ordered by the time.
Schema reminder
▼
Expected Results
start
name
2012-09-21 08:00:00
Tennis Court 1
2012-09-21 08:00:00
Tennis Court 2
2012-09-21 09:30:00
Tennis Court 1
2012-09-21 10:00:00
Tennis Court 2
2012-09-21 11:30:00
Tennis Court 2
2012-09-21 12:00:00
Tennis Court 1
2012-09-21 13:30:00
Tennis Court 1
2012-09-21 14:00:00
Tennis Court 2
2012-09-21 15:30:00
Tennis Court 1
2012-09-21 16:00:00
Tennis Court 2
2012-09-21 17:00:00
Tennis Court 1
2012-09-21 18:00:00
Tennis Court 2
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select bks.starttime as start, facs.name as name
from
cd.facilities facs
inner join cd.bookings bks
on facs.facid = bks.facid
where
facs.name in ('Tennis Court 2','Tennis Court 1') and
bks.starttime >= '2012-09-21' and
bks.starttime < '2012-09-22'
order by bks.starttime;
This is another
INNER JOIN
query, although it has a fair bit more complexity in it!  The
FROM
part of the query is easy - we're simply joining facilities and bookings tables together on the facid.  This produces a table where, for each row in bookings, we've attached detailed information about the facility being booked.
On to the
WHERE
component of the query.  The checks on starttime are fairly self explanatory - we're making sure that all the bookings start between the specified dates.  Since we're only interested in tennis courts, we're also using the
IN
operator to tell the database system to only give us back facility IDs 0 or 1 - the IDs of the courts.  There's other ways to express this: We could have used
where facs.facid = 0 or facs.facid = 1
, or even
where facs.name like 'Tennis%'
.
The rest is pretty simple: we
SELECT
the columns we're interested in, and
ORDER BY
the start time.
Previous Exercise
/
Joins
/
Simplejoin2
Next Exercise
This is another
INNER JOIN
. You may also want to think about using the
IN
or
LIKE
operators to limit the results you get back.
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
