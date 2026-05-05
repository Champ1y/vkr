---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/daysinmonth.html"
source_url: "https://pgexercises.com/questions/date/daysinmonth.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Work out the number of days in each month of 2012
Question
For each month of the year in 2012, output the number of days in that month.  Format the output as an integer column containing the month of the year, and a second column containing an interval data type.
Schema reminder
▼
Expected Results
month
length
1
31 days
2
29 days
3
31 days
4
30 days
5
31 days
6
30 days
7
31 days
8
31 days
9
30 days
10
31 days
11
30 days
12
31 days
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select 	extract(month from cal.month) as month,
(cal.month + interval '1 month') - cal.month as length
from
(
select generate_series(timestamp '2012-01-01', timestamp '2012-12-01', interval '1 month') as month
) cal
order by month;
This answer shows several of the concepts we've learned.  We use the
GENERATE_SERIES
function to produce a year's worth of timestamps, incrementing a month at a time.  We then use the
EXTRACT
function to get the month number.  Finally, we subtract each timestamp + 1 month from itself.
It's worth noting that subtracting two timestamps will always produce an interval in terms of days (or portions of a day).  You won't just get an answer in terms of months or years, because the length of those time periods is variable.
Previous Exercise
/
/
Daysinmonth
Next Exercise
Subtracting two timestamps will give you the interval you're looking for.  You can use the
EXTRACT
function to get the month from a timestamp.
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
