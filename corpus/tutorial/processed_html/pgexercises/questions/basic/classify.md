---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/classify.html"
source_url: "https://pgexercises.com/questions/basic/classify.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Classify results into buckets
Question
How can you produce a list of facilities, with each labelled as 'cheap' or 'expensive' depending on if their monthly maintenance cost is more than $100?  Return the name and monthly maintenance of the facilities in question.
Schema reminder
▼
Expected Results
name
cost
Tennis Court 1
expensive
Tennis Court 2
expensive
Badminton Court
cheap
Table Tennis
cheap
Massage Room 1
expensive
Massage Room 2
expensive
Squash Court
cheap
Snooker Table
cheap
Pool Table
cheap
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select name,
case when (monthlymaintenance > 100) then
'expensive'
else
'cheap'
end as cost
from cd.facilities;
This exercise contains a few new concepts.  The first is the fact that we're doing computation in the area of the query between
SELECT
and
FROM
.  Previously we've only used this to select columns that we want to return, but you can put anything in here that will produce a single result per returned row - including subqueries.
The second new concept is the
CASE
statement itself.
CASE
is effectively like if/switch statements in other languages, with a form as shown in the query.  To add a 'middling' option, we would simply insert another
when...then
section.
Finally, there's the
AS
operator.  This is simply used to label columns or expressions, to make them display more nicely or to make them easier to reference when used as part of a subquery.
Previous Exercise
/
/
Classify
Next Exercise
Try looking up the SQL
CASE
statement.
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
