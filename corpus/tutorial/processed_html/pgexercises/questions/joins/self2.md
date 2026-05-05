---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/self2.html"
source_url: "https://pgexercises.com/questions/joins/self2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a list of all members, along with their recommender
Question
How can you output a list of all members, including the individual who recommended them (if any)? Ensure that results are ordered by (surname, firstname).
Schema reminder
▼
Expected Results
memfname
memsname
recfname
recsname
Florence
Bader
Ponder
Stibbons
Anne
Baker
Ponder
Stibbons
Timothy
Baker
Jemima
Farrell
Tim
Boothe
Tim
Rownam
Gerald
Butters
Darren
Smith
Joan
Coplin
Timothy
Baker
Erica
Crumpet
Tracy
Smith
Nancy
Dare
Janice
Joplette
David
Farrell
Jemima
Farrell
GUEST
GUEST
Matthew
Genting
Gerald
Butters
John
Hunt
Millicent
Purview
David
Jones
Janice
Joplette
Douglas
Jones
David
Jones
Janice
Joplette
Darren
Smith
Anna
Mackenzie
Darren
Smith
Charles
Owen
Darren
Smith
David
Pinker
Jemima
Farrell
Millicent
Purview
Tracy
Smith
Tim
Rownam
Henrietta
Rumney
Matthew
Genting
Ramnaresh
Sarwin
Florence
Bader
Darren
Smith
Darren
Smith
Jack
Smith
Darren
Smith
Tracy
Smith
Ponder
Stibbons
Burton
Tracy
Burton
Tracy
Hyacinth
Tupperware
Henry
Worthington-Smyth
Tracy
Smith
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select mems.firstname as memfname, mems.surname as memsname, recs.firstname as recfname, recs.surname as recsname
from
cd.members mems
left outer join cd.members recs
on recs.memid = mems.recommendedby
order by memsname, memfname;
Let's introduce another new concept: the
LEFT OUTER JOIN
.  These are best explained by the way in which they differ from inner joins.  Inner joins take a left and a right table, and look for matching rows based on a join condition (
ON
).  When the condition is satisfied, a joined row is produced.  A
LEFT OUTER JOIN
operates similarly, except that if a given row on the left hand table doesn't match anything, it still produces an output row.  That output row consists of the left hand table row, and a bunch of
NULLS
in place of the right hand table row.
This is useful in situations like this question, where we want to produce output with optional data.  We want the names of all members, and the name of their recommender
if that person exists
.  You can't express that properly with an inner join.
As you may have guessed, there's other outer joins too.  The
RIGHT OUTER JOIN
is much like the
LEFT OUTER JOIN
, except that the left hand side of the expression is the one that contains the optional data.  The rarely-used
FULL OUTER JOIN
treats both sides of the expression as optional.
Previous Exercise
/
Joins
/
Self2
Next Exercise
Try investigating the
LEFT OUTER JOIN
.
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
