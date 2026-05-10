---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/facrev.html"
source_url: "https://pgexercises.com/questions/aggregates/facrev.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Find the total revenue of each facility
Question
Produce a list of facilities along with their total revenue.  The output table should consist of facility name and revenue, sorted by revenue.  Remember that there's a different cost for guests and members!
Schema reminder
▼
Expected Results
name
revenue
Table Tennis
180
Snooker Table
240
Pool Table
270
Badminton Court
1906.5
Squash Court
13468.0
Tennis Court 1
13860
Tennis Court 2
14310
Massage Room 2
15810
Massage Room 1
72540
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facs.name, sum(slots * case
when memid = 0 then facs.guestcost
else facs.membercost
end) as revenue
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.name
order by revenue;
The only real complexity in this query is that guests (member ID 0) have a different cost to everyone else.  We use a case statement to produce the cost for each session, and then sum each of those sessions, grouped by facility.
Previous Exercise
/
/
Facrev
Next Exercise
Remember the
CASE
statement!
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
