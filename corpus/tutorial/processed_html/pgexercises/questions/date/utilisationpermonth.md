---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/utilisationpermonth.html"
source_url: "https://pgexercises.com/questions/date/utilisationpermonth.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Next Category
Work out the utilisation percentage for each facility by month
Question
Work out the utilisation percentage for each facility by month, sorted by name and month, rounded to 1 decimal place.  Opening time is 8am, closing time is 8.30pm.  You can treat every month as a full month, regardless of if there were some dates the club was not open.
Schema reminder
▼
Expected Results
name
month
utilisation
Badminton Court
2012-07-01 00:00:00
23.2
Badminton Court
2012-08-01 00:00:00
59.2
Badminton Court
2012-09-01 00:00:00
76.0
Massage Room 1
2012-07-01 00:00:00
34.1
Massage Room 1
2012-08-01 00:00:00
63.5
Massage Room 1
2012-09-01 00:00:00
86.4
Massage Room 2
2012-07-01 00:00:00
3.1
Massage Room 2
2012-08-01 00:00:00
10.6
Massage Room 2
2012-09-01 00:00:00
16.3
Pool Table
2012-07-01 00:00:00
15.1
Pool Table
2012-08-01 00:00:00
41.5
Pool Table
2012-09-01 00:00:00
62.8
Pool Table
2013-01-01 00:00:00
0.1
Snooker Table
2012-07-01 00:00:00
20.1
Snooker Table
2012-08-01 00:00:00
42.1
Snooker Table
2012-09-01 00:00:00
56.8
Squash Court
2012-07-01 00:00:00
21.2
Squash Court
2012-08-01 00:00:00
51.6
Squash Court
2012-09-01 00:00:00
72.0
Table Tennis
2012-07-01 00:00:00
13.4
Table Tennis
2012-08-01 00:00:00
39.2
Table Tennis
2012-09-01 00:00:00
56.3
Tennis Court 1
2012-07-01 00:00:00
34.8
Tennis Court 1
2012-08-01 00:00:00
59.2
Tennis Court 1
2012-09-01 00:00:00
78.8
Tennis Court 2
2012-07-01 00:00:00
26.7
Tennis Court 2
2012-08-01 00:00:00
62.3
Tennis Court 2
2012-09-01 00:00:00
78.4
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select name, month,
round((100*slots)/
cast(
25*(cast((month + interval '1 month') as date)
- cast (month as date)) as numeric),1) as utilisation
from  (
select facs.name as name, date_trunc('month', starttime) as month, sum(slots) as slots
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.facid, month
) as inn
order by name, month
The meat of this query (the inner subquery) is really quite simple: an aggregation to work out the total number of slots used per facility per month.  If you've covered the rest of this section and the category on aggregates, you likely didn't find this bit too challenging.
This query does, unfortunately, have some other complexity in it: working out the number of days in each month.  We can calculate the number of days between two months by subtracting two timestamps with a month between them.  This, unfortunately, gives us back on interval datatype, which we can't use to do mathematics.  In this case we've worked around that limitation by converting our timestamps into
dates
before subtracting.  Subtracting date types gives us an integer number of days.
A alternative to this workaround is to convert the interval into an
epoch
value: that is, a number of seconds.  To do this use
EXTRACT(EPOCH FROM month)/(24*60*60)
.  This is arguably a much nicer way to do things, but is much less portable to other database systems.
Previous Exercise
/
/
Utilisationpermonth
Next Category
Remember different months have different lengths - you'll need to calculate the number of available slots in each month.  You need to find a way to retrieve an
integer
(rather than interval) number of days for the length of the month.
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
