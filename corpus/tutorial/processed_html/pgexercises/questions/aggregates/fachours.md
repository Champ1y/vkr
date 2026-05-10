---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachours.html"
source_url: "https://pgexercises.com/questions/aggregates/fachours.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

List the total slots booked per facility
Question
Produce a list of the total number of slots booked per facility.  For now, just produce an output table consisting of facility id and slots, sorted by facility id.
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
3
830
4
1404
5
228
6
1104
7
908
8
911
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
order by facid;
Other than the fact that we've introduced the
SUM
aggregate function, there's not a great deal to say about this exercise.  For each distinct facility id, the
SUM
function adds together everything in the slots column.
Previous Exercise
/
/
Fachours
Next Exercise
For this one you'll need to check out the
SUM
aggregate function.
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
