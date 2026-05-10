---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/payback.html"
source_url: "https://pgexercises.com/questions/aggregates/payback.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Calculate the payback time for each facility
Question
Based on the 3 complete months of data so far, calculate the amount of time each facility will take to repay its cost of ownership.  Remember to take into account ongoing monthly maintenance.  Output facility name and payback time in months, order by facility name.  Don't worry about differences in month lengths, we're only looking for a rough value here!
Schema reminder
▼
Expected Results
name
months
Badminton Court
6.8317677198975235
Massage Room 1
0.18885741265344664778
Massage Room 2
1.7621145374449339
Pool Table
5.3333333333333333
Snooker Table
6.9230769230769231
Squash Court
1.1339582703356516
Table Tennis
6.4000000000000000
Tennis Court 1
2.2624434389140271
Tennis Court 2
1.7505470459518600
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select 	facs.name as name,
facs.initialoutlay/((sum(case
when memid = 0 then slots * facs.guestcost
else slots * membercost
end)/3) - facs.monthlymaintenance) as months
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.facid
order by name;
In contrast to all our recent exercises, there's no need to use window functions to solve this problem: it's just a bit of maths involving monthly revenue, initial outlay, and monthly maintenance.  Again, for production code you might want to clarify what's going on a little here using a subquery (although since we've hard-coded the number of months, putting this into production is unlikely!).  A tidied-up version might look like:
select 	name,
initialoutlay / (monthlyrevenue - monthlymaintenance) as repaytime
from
(select facs.name as name,
facs.initialoutlay as initialoutlay,
facs.monthlymaintenance as monthlymaintenance,
sum(case
when memid = 0 then slots * facs.guestcost
else slots * membercost
end)/3 as monthlyrevenue
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.facid
) as subq
order by name;
But, I hear you ask, what would an automatic version of this look like?  One that didn't need to have a hard-coded number of months in it?  That's a little more complicated, and involves some date arithmetic.  I've factored that out into a CTE to make it a little more clear.
with monthdata as (
select 	mincompletemonth,
maxcompletemonth,
(extract(year from maxcompletemonth)*12) +
extract(month from maxcompletemonth) -
(extract(year from mincompletemonth)*12) -
extract(month from mincompletemonth) as nummonths
from (
select 	date_trunc('month',
(select max(starttime) from cd.bookings)) as maxcompletemonth,
date_trunc('month',
(select min(starttime) from cd.bookings)) as mincompletemonth
) as subq
)
select 	name,
initialoutlay / (monthlyrevenue - monthlymaintenance) as repaytime

from
(select facs.name as name,
facs.initialoutlay as initialoutlay,
facs.monthlymaintenance as monthlymaintenance,
sum(case
when memid = 0 then slots * facs.guestcost
else slots * membercost
end)/(select nummonths from monthdata) as monthlyrevenue

from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
where bks.starttime < (select maxcompletemonth from monthdata)
group by facs.facid
) as subq
order by name;
This code restricts the data that goes in to complete months.  It does this by selecting the maximum date, rounding down to the month, and stripping out all dates larger than that.  Even this code is not completely-complete.  It doesn't handle the case of a facility making a loss.  Fixing that is not too hard, and is left as (another) exercise for the reader!
Previous Exercise
/
/
Payback
Next Exercise
There's no need to use window functions to solve this problem.  Hard-code the number of months for an easy time, calculate them for a tougher one.
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
