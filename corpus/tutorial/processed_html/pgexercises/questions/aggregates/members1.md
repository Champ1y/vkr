---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/members1.html"
source_url: "https://pgexercises.com/questions/aggregates/members1.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Find the count of members who have made at least one booking
Question
Find the total number of members (including guests) who have made at least one booking.
Schema reminder
▼
Expected Results
count
30
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select count(distinct memid) from cd.bookings
Your first instinct may be to go for a subquery here.  Something like the below:
select count(*) from
(select distinct memid from cd.bookings) as mems
This does work perfectly well, but we can simplify a touch with the help of a little extra knowledge in the form of
COUNT DISTINCT
.  This does what you might expect, counting the distinct values in the passed column.
Previous Exercise
/
/
Members1
Next Exercise
Take a look at
COUNT DISTINCT
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
