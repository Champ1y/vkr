---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/recursive/getdownward.html"
source_url: "https://pgexercises.com/questions/recursive/getdownward.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Find the downward recommendation chain for member ID 1
Question
Find the downward recommendation chain for member ID 1: that is, the members they recommended, the members those members recommended, and so on.  Return member ID and name, and order by ascending member id.
Schema reminder
▼
Expected Results
memid
firstname
surname
4
Janice
Joplette
5
Gerald
Butters
7
Nancy
Dare
10
Charles
Owen
11
David
Jones
14
Jack
Smith
20
Matthew
Genting
21
Anna
Mackenzie
26
Douglas
Jones
27
Henrietta
Rumney
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
with recursive recommendeds(memid) as (
select memid from cd.members where recommendedby = 1
union all
select mems.memid
from recommendeds recs
inner join cd.members mems
on mems.recommendedby = recs.memid
)
select recs.memid, mems.firstname, mems.surname
from recommendeds recs
inner join cd.members mems
on recs.memid = mems.memid
order by memid
This is a pretty minor variation on the previous question.  The essential difference is that we're now heading in the opposite direction.  One interesting point to note is that unlike the previous example, this CTE produces multiple rows per iteration, by virtue of the fact that we're heading down the recommendation tree (following all branches) rather than up it.
Previous Exercise
/
/
Getdownward
Next Exercise
Read up on
WITH RECURSIVE
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
