---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/where4.html"
source_url: "https://pgexercises.com/questions/basic/where4.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Matching against multiple possible values
Question
How can you retrieve the details of facilities with ID 1 and 5?  Try to do it without using the
OR
operator.
Schema reminder
▼
Expected Results
facid
name
membercost
guestcost
initialoutlay
monthlymaintenance
1
Tennis Court 2
5
25
8000
200
5
Massage Room 2
35
80
4000
3000
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select *
from cd.facilities
where
facid in (1,5);
The obvious answer to this question is to use a
WHERE
clause that looks like
where facid = 1 or facid = 5
.  An alternative that is easier with large numbers of possible matches is the
IN
operator.  The
IN
operator takes a list of possible values, and matches them against (in this case) the facid. If one of the values matches, the where clause is true for that row, and the row is returned.
The
IN
operator is a good early demonstrator of the elegance of the relational model.  The argument it takes is not just a list of values - it's actually a table with a single column.  Since queries also return tables, if you create a query that returns a single column, you can feed those results into an
IN
operator.  To give a toy example:
select *
from cd.facilities
where
facid in (
select facid from cd.facilities
);
This example is functionally equivalent to just selecting all the facilities, but shows you how to feed the results of one query into another.  The inner query is called a
subquery
.
Previous Exercise
/
/
Where4
Next Exercise
Try looking up the SQL
IN
operator.
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
