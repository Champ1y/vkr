---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/count3.html"
source_url: "https://pgexercises.com/questions/aggregates/count3.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Count the number of recommendations each member makes.
Question
Produce a count of the number of recommendations each member has made.  Order by member ID.
Schema reminder
▼
Expected Results
recommendedby
count
1
5
2
3
3
1
4
2
5
1
6
1
9
2
11
1
13
2
15
1
16
1
20
1
30
1
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select recommendedby, count(*)
from cd.members
where recommendedby is not null
group by recommendedby
order by recommendedby;
Previously, we've seen that aggregation functions are applied to a column of values, and convert them into an aggregated scalar value.  This is useful, but we often find that we don't want just a single aggregated result: for example, instead of knowing the total amount of money the club has made this month, I might want to know how much money each different facility has made, or which times of day were most lucrative.
In order to support this kind of behaviour, SQL has the
GROUP BY
construct.  What this does is batch the data together into groups, and run the aggregation function separately for each group.  When you specify a
GROUP BY
, the database produces an aggregated value for each distinct value in the supplied columns.  In this case, we're saying 'for each distinct value of recommendedby, get me the number of times that value appears'.
Previous Exercise
/
/
Count3
Next Exercise
Try investigating
GROUP BY
with your count this time.  Don't forget to filter out null recommenders!
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
