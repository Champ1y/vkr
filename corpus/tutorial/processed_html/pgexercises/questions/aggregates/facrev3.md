---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/facrev3.html"
source_url: "https://pgexercises.com/questions/aggregates/facrev3.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Find the top three revenue generating facilities
Question
Produce a list of the top three revenue generating facilities (including ties).  Output facility name and rank, sorted by rank and facility name.
Schema reminder
▼
Expected Results
name
rank
Massage Room 1
1
Massage Room 2
2
Tennis Court 2
3
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select name, rank from (
select facs.name as name, rank() over (order by sum(case
when memid = 0 then slots * facs.guestcost
else slots * membercost
end) desc) as rank
from cd.bookings bks
inner join cd.facilities facs
on bks.facid = facs.facid
group by facs.name
) as subq
where rank <= 3
order by rank;
This question doesn't introduce any new concepts, and is just intended to give you the opportunity to practise what you already know.  We use the
CASE
statement to calculate the revenue for each slot, and aggregate that on a per-facility basis using
SUM
.  We then use the
RANK
window function to produce a ranking, wrap it all up in a subquery, and extract everything with a rank less than or equal to 3.
Previous Exercise
/
/
Facrev3
Next Exercise
Yet another question based on the
RANK
window function!  Remember the relative complexity of calculating the revenue of a facility, since you need to count for the different costs for the GUEST user..
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
