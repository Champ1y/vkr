---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachoursbymonth3.html"
source_url: "https://pgexercises.com/questions/aggregates/fachoursbymonth3.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

List the total slots booked per facility per month, part 2
Question
Produce a list of the total number of slots booked per facility per month in the year of 2012.  In this version, include output rows containing totals for all months per facility, and a total for all months for all facilities.  The output table should consist of facility id, month and slots, sorted by the id and month.  When calculating the aggregated values for all months and all facids, return null values in the month and facid columns.
Schema reminder
▼
Expected Results
facid
month
slots
0
7
270
0
8
459
0
9
591
0
1320
1
7
207
1
8
483
1
9
588
1
1278
2
7
180
2
8
459
2
9
570
2
1209
3
7
104
3
8
304
3
9
422
3
830
4
7
264
4
8
492
4
9
648
4
1404
5
7
24
5
8
82
5
9
122
5
228
6
7
164
6
8
400
6
9
540
6
1104
7
7
156
7
8
326
7
9
426
7
908
8
7
117
8
8
322
8
9
471
8
910
9191
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, extract(month from starttime) as month, sum(slots) as slots
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
group by rollup(facid, month)
order by facid, month;
When we are doing data analysis, we sometimes want to perform multiple levels of aggregation to allow ourselves to 'zoom' in and out to different depths. In this case, we might be looking at each facility's overall usage, but then want to dive in to see how they've performed on a per-month basis. Using the SQL we know so far, it's quite cumbersome to produce a single query that does what we want - we effectively have to resort to concatenating multiple queries using UNION ALL:
select facid, extract(month from starttime) as month, sum(slots) as slots
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
group by facid, month
union all
select facid, null, sum(slots) as slots
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
group by facid
union all
select null, null, sum(slots) as slots
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
order by facid, month;
As you can see, each subquery performs a different level of aggregation, and we just combine the results. We can clean this up a lot by factoring out commonalities using a CTE:
with bookings as (
select facid, extract(month from starttime) as month, slots
from cd.bookings
where
starttime >= '2012-01-01'
and starttime < '2013-01-01'
)
select facid, month, sum(slots) from bookings group by facid, month
union all
select facid, null, sum(slots) from bookings group by facid
union all
select null, null, sum(slots) from bookings
order by facid, month;
This version is not excessively hard on the eyes, but it becomes cumbersome as the number of aggregation columns increases. Fortunately, PostgreSQL 9.5 introduced support for the
ROLLUP
operator, which we've used to simplify our accepted answer.
ROLLUP
produces a hierarchy of aggregations in the order passed into it: for example,
ROLLUP(facid, month)
outputs aggregations on (facid, month), (facid), and (). If we wanted an aggregation of all facilities for a month (instead of all months for a facility) we'd have to reverse the order, using
ROLLUP(month, facid)
. Alternatively, if we instead want all possible permutations of the columns we pass in, we can use
CUBE
rather than
ROLLUP
. This will produce (facid, month), (month), (facid), and ().
ROLLUP
and
CUBE
are special cases of
GROUPING SETS
.
GROUPING SETS
allow you to specify the exact aggregation permutations you want: you could, for example, ask for just (facid, month) and (facid), skipping the top-level aggregation.
Previous Exercise
/
/
Fachoursbymonth3
Next Exercise
Look up Postgres'
ROLLUP
operator.
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
