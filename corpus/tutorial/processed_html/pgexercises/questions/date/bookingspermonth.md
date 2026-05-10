---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/bookingspermonth.html"
source_url: "https://pgexercises.com/questions/date/bookingspermonth.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Return a count of bookings for each month
Question
Return a count of bookings for each month, sorted by month
Schema reminder
▼
Expected Results
month
count
2012-07-01 00:00:00
658
2012-08-01 00:00:00
1472
2012-09-01 00:00:00
1913
2013-01-01 00:00:00
1
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select date_trunc('month', starttime) as month, count(*)
from cd.bookings
group by month
order by month
This one is a fairly simple reuse of concepts we've seen before.  We simply count the number of bookings, and aggregate by the booking's start time, truncated to the month.
Previous Exercise
/
/
Bookingspermonth
Next Exercise
You're probably going to want the date_trunc function again.
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
