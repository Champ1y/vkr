---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/where3.html"
source_url: "https://pgexercises.com/questions/basic/where3.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Basic string searches
Question
How can you produce a list of all facilities with the word 'Tennis' in their name?
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
3
Table Tennis
0
5
320
10
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
name like '%Tennis%';
SQL's
LIKE
operator provides simple pattern matching on strings.  It's pretty much universally implemented, and is nice and simple to use - it just takes a string with the
%
character matching any string, and
_
matching any single character.  In this case, we're looking for names containing the word 'Tennis', so putting a % on either side fits the bill.
There's other ways to accomplish this task: Postgres supports regular expressions with the
~
operator, for example.  Use whatever makes you feel comfortable, but do be aware that the
LIKE
operator is much more portable between systems.
Previous Exercise
/
/
Where3
Next Exercise
Try looking up the SQL
LIKE
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
