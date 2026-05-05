---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/series.html"
source_url: "https://pgexercises.com/questions/date/series.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Generate a list of all the dates in October 2012
Question
Produce a list of all the dates in October 2012.  They can be output as a timestamp (with time set to midnight) or a date.
Schema reminder
▼
Expected Results
ts
2012-10-01 00:00:00
2012-10-02 00:00:00
2012-10-03 00:00:00
2012-10-04 00:00:00
2012-10-05 00:00:00
2012-10-06 00:00:00
2012-10-07 00:00:00
2012-10-08 00:00:00
2012-10-09 00:00:00
2012-10-10 00:00:00
2012-10-11 00:00:00
2012-10-12 00:00:00
2012-10-13 00:00:00
2012-10-14 00:00:00
2012-10-15 00:00:00
2012-10-16 00:00:00
2012-10-17 00:00:00
2012-10-18 00:00:00
2012-10-19 00:00:00
2012-10-20 00:00:00
2012-10-21 00:00:00
2012-10-22 00:00:00
2012-10-23 00:00:00
2012-10-24 00:00:00
2012-10-25 00:00:00
2012-10-26 00:00:00
2012-10-27 00:00:00
2012-10-28 00:00:00
2012-10-29 00:00:00
2012-10-30 00:00:00
2012-10-31 00:00:00
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select generate_series(timestamp '2012-10-01', timestamp '2012-10-31', interval '1 day') as ts;
One of the best features of Postgres over other DBs is a simple function called
GENERATE_SERIES
.  This function allows you to generate a list of dates or numbers, specifying a start, an end, and an increment value.  It's extremely useful for situations where you want to output, say, sales per day over the course of a month.  A typical way to do that on a table containing a list of sales might be to use a
SUM
aggregation, grouping by the date and product type.  Unfortunately, this approach has a flaw: if there are no sales for a given day, it won't show up!  To make it work properly, you need to left join from a sequential list of timestamps to the aggregated data to fill in the blank spaces.
On other database systems, it's not uncommon to keep a 'calendar table' full of dates, with which you can perform these joins.  Alternatively, on some systems you can write an analogue to generate_series using recursive CTEs.  Fortunately for us, Postgres makes our lives a lot easier!
Previous Exercise
/
/
Series
Next Exercise
Take a look at Postgres'
GENERATE_SERIES
function
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
