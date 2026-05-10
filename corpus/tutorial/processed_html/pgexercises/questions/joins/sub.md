---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/sub.html"
source_url: "https://pgexercises.com/questions/joins/sub.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a list of all members, along with their recommender, using no joins.
Question
How can you output a list of all members, including the individual who recommended them (if any), without using any joins? Ensure that there are no duplicates in the list, and that each firstname + surname pairing is formatted as a column and ordered.
Schema reminder
▼
Expected Results
member
recommender
Anna Mackenzie
Darren Smith
Anne Baker
Ponder Stibbons
Burton Tracy
Charles Owen
Darren Smith
Darren Smith
David Farrell
David Jones
Janice Joplette
David Pinker
Jemima Farrell
Douglas Jones
David Jones
Erica Crumpet
Tracy Smith
Florence Bader
Ponder Stibbons
GUEST GUEST
Gerald Butters
Darren Smith
Henrietta Rumney
Matthew Genting
Henry Worthington-Smyth
Tracy Smith
Hyacinth Tupperware
Jack Smith
Darren Smith
Janice Joplette
Darren Smith
Jemima Farrell
Joan Coplin
Timothy Baker
John Hunt
Millicent Purview
Matthew Genting
Gerald Butters
Millicent Purview
Tracy Smith
Nancy Dare
Janice Joplette
Ponder Stibbons
Burton Tracy
Ramnaresh Sarwin
Florence Bader
Tim Boothe
Tim Rownam
Tim Rownam
Timothy Baker
Jemima Farrell
Tracy Smith
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select distinct mems.firstname || ' ' ||  mems.surname as member,
(select recs.firstname || ' ' || recs.surname as recommender
from cd.members recs
where recs.memid = mems.recommendedby
)
from
cd.members mems
order by member;
This exercise marks the introduction of subqueries.  Subqueries are, as the name implies, queries within a query.  They're commonly used with aggregates, to answer questions like 'get me all the details of the member who has spent the most hours on Tennis Court 1'.
In this case, we're simply using the subquery to emulate an outer join.  For every value of member, the subquery is run once to find the name of the individual who recommended them (if any).  A subquery that uses information from the outer query in this way (and thus has to be run for each row in the result set) is known as a
correlated subquery
.
Previous Exercise
/
Joins
/
Sub
Next Exercise
Answering this question correctly requires the use of a
subquery
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
