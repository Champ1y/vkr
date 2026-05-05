---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/classify.html"
source_url: "https://pgexercises.com/questions/aggregates/classify.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Classify facilities by value
Question
Classify facilities into equally sized groups of high, average, and low based on their revenue. Order by classification and facility name.
Schema reminder
▼
Expected Results
name
revenue
Massage Room 1
high
Massage Room 2
high
Tennis Court 2
high
Badminton Court
average
Squash Court
average
Tennis Court 1
average
Pool Table
low
Snooker Table
low
Table Tennis
low
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select name, case when class=1 then 'high'
when class=2 then 'average'
else 'low'
end revenue
from (
select facs.name as name, ntile(3) over (order by sum(case
when memid = 0 then slots * facs.guestcost
else slots * membercost
end) desc) as class
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.name
) as subq
order by class, name;
This exercise should mostly use familiar concepts, although we do introduce the
NTILE
window function.
NTILE
groups values into a passed-in number of groups, as evenly as possible.  It outputs a number from 1->number of groups.  We then use a
CASE
statement to turn that number into a label!
Previous Exercise
/
/
Classify
Next Exercise
Investigate the
NTILE
window function.
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
