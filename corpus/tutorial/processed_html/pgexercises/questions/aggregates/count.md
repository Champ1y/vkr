---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/count.html"
source_url: "https://pgexercises.com/questions/aggregates/count.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Question
For our first foray into aggregates, we're going to stick to something simple.  We want to know how many facilities exist - simply produce a total count.
Schema reminder
▼
Expected Results
count
9
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select count(*) from cd.facilities;
Aggregation starts out pretty simply!  The SQL above selects everything from our facilities table, and then counts the number of rows in the result set.  The count function has a variety of uses:
COUNT(*)
simply returns the number of rows
COUNT(address)
counts the number of non-null addresses in the result set.
Finally,
COUNT(DISTINCT address)
counts the number of
different
addresses in the facilities table.
The basic idea of an aggregate function is that it takes in a column of data, performs some function upon it, and outputs a
scalar
(single) value.  There are a bunch more aggregation functions, including
MAX
,
MIN
,
SUM
, and
AVG
.  These all do pretty much what you'd expect from their names :-).
One aspect of aggregate functions that people often find confusing is in queries like the below:
select facid, count(*) from cd.facilities
Try it out, and you'll find that it doesn't work.  This is because count(*) wants to collapse the facilities table into a single value - unfortunately, it can't do that, because there's a lot of different facids in cd.facilities - Postgres doesn't know which facid to pair the count with.
Instead, if you wanted a query that returns all the facids along with a count on each row, you can break the aggregation out into a subquery as below:
select facid,
(select count(*) from cd.facilities)
from cd.facilities
When we have a subquery that returns a scalar value like this, Postgres knows to simply repeat the value for every row in cd.facilities.
/
/
Count
Next Exercise
Try investigating the SQL
COUNT
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
