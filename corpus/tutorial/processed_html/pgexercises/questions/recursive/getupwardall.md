---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/recursive/getupwardall.html"
source_url: "https://pgexercises.com/questions/recursive/getupwardall.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Questions Complete!
Produce a CTE that can return the upward recommendation chain for any member
Question
Produce a CTE that can return the upward recommendation chain for any member.  You should be able to
select recommender from recommenders where member=x
.  Demonstrate it by getting the chains for members 12 and 22.  Results table should have member and recommender, ordered by member ascending, recommender descending.
Schema reminder
▼
Expected Results
member
recommender
firstname
surname
12
9
Ponder
Stibbons
12
6
Burton
Tracy
22
16
Timothy
Baker
22
13
Jemima
Farrell
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
with recursive recommenders(recommender, member) as (
select recommendedby, memid
from cd.members
union all
select mems.recommendedby, recs.member
from recommenders recs
inner join cd.members mems
on mems.memid = recs.recommender
)
select recs.member member, recs.recommender, mems.firstname, mems.surname
from recommenders recs
inner join cd.members mems
on recs.recommender = mems.memid
where recs.member = 22 or recs.member = 12
order by recs.member asc, recs.recommender desc
This question requires us to produce a CTE that can calculate the upward recommendation chain for any user.  Most of the complexity of working out the answer is in realising that we now need our CTE to produce two columns: one to contain the member we're asking about, and another to contain the members in their recommendation tree.  Essentially what we're doing is producing a table that flattens out the recommendation hierarchy.
Since we're looking to produce the chain for every user, our initial statement needs to select data for each user: their ID and who recommended them.  Subsequently, we want to pass the member field through each iteration without changing it, while getting the next recommender.  You can see that the recursive part of our statement hasn't really changed, except to pass through the 'member' field.
Previous Exercise
/
/
Getupwardall
Questions Complete!
Your initial statement should return all the recommendedby and memid fields in the members table.
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
