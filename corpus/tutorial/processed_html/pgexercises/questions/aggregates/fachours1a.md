---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachours1a.html"
source_url: "https://pgexercises.com/questions/aggregates/fachours1a.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

List facilities with more than 1000 slots booked
Question
Produce a list of facilities with more than 1000 slots booked.  Produce an output table consisting of facility id and slots, sorted by facility id.
Schema reminder
▼
Expected Results
facid
Total Slots
0
1320
1
1278
2
1209
4
1404
6
1104
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, sum(slots) as "Total Slots"
from cd.bookings
group by facid
having sum(slots) > 1000
order by facid
It turns out that there's actually an SQL keyword designed to help with the filtering of output from aggregate functions.  This keyword is
HAVING
.
The behaviour of
HAVING
is easily confused with that of
WHERE
.  The best way to think about it is that in the context of a query with an aggregate function,
WHERE
is used to filter what data gets input into the aggregate function, while
HAVING
is used to filter the data once it is output from the function. Try experimenting to explore this difference!
Previous Exercise
/
/
Fachours1a
Next Exercise
Try investigating the
HAVING
clause.
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
