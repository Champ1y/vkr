---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachoursbymonth2.html"
source_url: "https://pgexercises.com/questions/aggregates/fachoursbymonth2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

List the total slots booked per facility per month
Question
Produce a list of the total number of slots booked per facility per month in the year of 2012.  Produce an output table consisting of facility id and slots, sorted by the id and month.
Schema reminder
▼
Expected Results
facid
month
Total Slots
0
7
270
0
8
459
0
9
591
1
7
207
1
8
483
1
9
588
2
7
180
2
8
459
2
9
570
3
7
104
3
8
304
3
9
422
4
7
264
4
8
492
4
9
648
5
7
24
5
8
82
5
9
122
6
7
164
6
8
400
6
9
540
7
7
156
7
8
326
7
9
426
8
7
117
8
8
322
8
9
471
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, extract(month from starttime) as month, sum(slots) as "Total Slots"
from cd.bookings
where extract(year from starttime) = 2012
group by facid, month
order by facid, month;
The main piece of new functionality in this question is the
EXTRACT
function.
EXTRACT
allows you to get individual components of a timestamp, like day, month, year, etc.  We group by the output of this function to provide per-month values.  An alternative, if we needed to distinguish between the same month in different years, is to make use of the
DATE_TRUNC
function, which truncates a date to a given granularity. It's also worth noting that this is the first time we've truly made use of the ability to group by more than one column.
One thing worth considering with this answer: the use of the
EXTRACT
function in the
WHERE
clause has the potential to cause severe issues with performance on larger tables. If the timestamp column has a regular index on it, Postgres will not understand that it can use the index to speed up the query and will instead have to scan through the whole table. You've got a couple of options here:
Consider creating an
expression-based index
on the timestamp column. With appropriately specified indexes Postgres can use indexes to speed up
WHERE
clauses containing function calls.
Alter the query to be a little more verbose, but use more standard comparisons, for example:
select facid, extract(month from starttime) as month, sum(slots) as "Total Slots"
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
group by facid, month
order by facid, month;
Postgres is able to use an index using these standard comparisons without any additional assistance.
Previous Exercise
/
/
Fachoursbymonth2
Next Exercise
Take a look at the
EXTRACT
function.
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
