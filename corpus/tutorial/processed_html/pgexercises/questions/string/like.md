---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/like.html"
source_url: "https://pgexercises.com/questions/string/like.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Find facilities by a name prefix
Question
Find all facilities whose name begins with 'Tennis'.  Retrieve all columns.
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
select * from cd.facilities where name like 'Tennis%';
The SQL
LIKE
operator is a highly standard way of searching for a string using basic matching.  The
%
character matches any string, while
_
matches any single character.
One point that's worth considering when you use
LIKE
is how it uses indexes.  If you're using the 'C'
locale
, any
LIKE
string with a fixed beginning (as in our example here) can use an index.  If you're using any other locale,
LIKE
will not use any index by default.  See
here
for details on how to change that.
Previous Exercise
/
/
Like
Next Exercise
Use the
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
