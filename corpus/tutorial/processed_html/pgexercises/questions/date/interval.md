---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/interval.html"
source_url: "https://pgexercises.com/questions/date/interval.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Subtract timestamps from each other
Question
Find the result of subtracting the timestamp '2012-07-30 01:00:00' from the timestamp '2012-08-31 01:00:00'
Schema reminder
▼
Expected Results
interval
32 days
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select timestamp '2012-08-31 01:00:00' - timestamp '2012-07-30 01:00:00' as interval;
Subtracting timestamps produces an
INTERVAL
data type.
INTERVAL
s are a special data type for representing the difference between two
TIMESTAMP
types.  When subtracting timestamps, Postgres will typically give an interval in terms of days, hours, minutes, seconds, without venturing into months.  This generally makes life easier, since months are of variable lengths.
One of the useful things about intervals, though, is the fact that they
can
encode months.  Let's imagine that I want to schedule something to occur in exactly one month's time, regardless of the length of my month.  To do this, I could use
[timestamp] + interval '1 month'
.
Intervals stand in contrast to SQL's treatment of
types.  Dates don't use intervals - instead, subtracting two dates will return an integer representing the number of days between the two dates.  You can also add integer values to dates.  This is sometimes more convenient, depending on how much intelligence you require in the handling of your dates!
Previous Exercise
/
/
Interval
Next Exercise
You can use the '-' symbol on timestamps
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
