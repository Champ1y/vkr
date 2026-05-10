---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/union.html"
source_url: "https://pgexercises.com/questions/basic/union.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Combining results from multiple queries
Question
You, for some reason, want a combined list of all surnames and all facility names.  Yes, this is a contrived example :-).  Produce that list!
Schema reminder
▼
Expected Results
surname
Tennis Court 2
Worthington-Smyth
Badminton Court
Pinker
Dare
Bader
Mackenzie
Crumpet
Massage Room 1
Squash Court
Tracy
Hunt
Tupperware
Smith
Butters
Rownam
Baker
Genting
Purview
Coplin
Massage Room 2
Joplette
Stibbons
Rumney
Pool Table
Sarwin
Boothe
Farrell
Tennis Court 1
Snooker Table
Owen
Table Tennis
GUEST
Jones
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select surname
from cd.members
union
select name
from cd.facilities;
The
UNION
operator does what you might expect: combines the results of two SQL queries into a single table.  The caveat is that both results from the two queries must have the same number of columns and compatible data types.
UNION
removes duplicate rows, while
UNION ALL
does not.  Use
UNION ALL
by default, unless you care about duplicate results.
Previous Exercise
/
/
Union
Next Exercise
Look up the SQL keyword
UNION
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
