---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/case.html"
source_url: "https://pgexercises.com/questions/string/case.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Perform a case-insensitive search
Question
Perform a case-insensitive search to find all facilities whose name begins with 'tennis'.  Retrieve all columns.
Schema reminder
▼
Expected Results
facid
name
membercost
guestcost
initialoutlay
monthlymaintenance
0
Tennis Court 1
5
25
10000
200
1
Tennis Court 2
5
25
8000
200
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select * from cd.facilities where upper(name) like 'TENNIS%';
There's no direct operator for case-insensitive comparison in standard SQL.  Fortunately, we can take a page from many other language's books, and simply force all values into upper case when we do our comparison.  This renders case irrelevant, and gives us our result.
Alternatively, Postgres does provide the
ILIKE
operator, which performs case insensitive searches.  This isn't standard SQL, but it's arguably more clear.
You should realise that running a function like
UPPER
over a column value prevents Postgres from making use of any indexes on the column (the same is true for
ILIKE
).  Fortunately, Postgres has got your back: rather than simply creating indexes over columns, you can also create indexes over
expressions
.  If you created an index over
UPPER(name)
, this query could use it quite happily.
Previous Exercise
/
/
Case
Next Exercise
Use the
UPPER
function or the
ILIKE
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
