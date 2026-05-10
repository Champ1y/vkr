---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/self.html"
source_url: "https://pgexercises.com/questions/joins/self.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a list of all members who have recommended another member
Question
How can you output a list of all members who have recommended another member?  Ensure that there are no duplicates in the list, and that results are ordered by (surname, firstname).
Schema reminder
▼
Expected Results
firstname
surname
Florence
Bader
Timothy
Baker
Gerald
Butters
Jemima
Farrell
Matthew
Genting
David
Jones
Janice
Joplette
Millicent
Purview
Tim
Rownam
Darren
Smith
Tracy
Smith
Ponder
Stibbons
Burton
Tracy
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select distinct recs.firstname as firstname, recs.surname as surname
from
cd.members mems
inner join cd.members recs
on recs.memid = mems.recommendedby
order by surname, firstname;
Here's a concept that some people find confusing: you can join a table to itself!  This is really useful if you have columns that reference data in the same table, like we do with recommendedby in cd.members.
If you're having trouble visualising this, remember that this works just the same as any other inner join.  Our join takes each row in members that has a recommendedby value, and looks in members again for the row which has a matching member id.  It then generates an output row combining the two members entries.  This looks like the diagram below:
Note that while we might have two 'surname' columns in the output set, they can be distinguished by their table aliases.  Once we've selected the columns that we want, we simply use
DISTINCT
to ensure that there are no duplicates.
Previous Exercise
/
Joins
/
Self
Next Exercise
This is an
INNER JOIN
, just like the previous exercises.
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
