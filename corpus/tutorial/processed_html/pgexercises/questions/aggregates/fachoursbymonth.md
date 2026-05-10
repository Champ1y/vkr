---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachoursbymonth.html"
source_url: "https://pgexercises.com/questions/aggregates/fachoursbymonth.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

List the total slots booked per facility in a given month
Question
Produce a list of the total number of slots booked per facility in the month of September 2012.  Produce an output table consisting of facility id and slots, sorted by the number of slots.
Schema reminder
▼
Expected Results
facid
Total Slots
5
122
3
422
7
426
8
471
6
540
2
570
1
588
0
591
4
648
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, sum(slots) as "Total Slots"
from cd.bookings
where
starttime >= '2012-09-01'
and starttime < '2012-10-01'
group by facid
order by sum(slots);
This is only a minor alteration of our previous example.  Remember that aggregation happens after the
WHERE
clause is evaluated: we thus use the
WHERE
to restrict the data we aggregate over, and our aggregation only sees data from a single month.
Previous Exercise
/
/
Fachoursbymonth
Next Exercise
You can restrict the data that goes into your aggregate functions using the
WHERE
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
