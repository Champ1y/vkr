---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/count2.html"
source_url: "https://pgexercises.com/questions/aggregates/count2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Count the number of expensive facilities
Question
Produce a count of the number of facilities that have a cost to guests of 10 or more.
Schema reminder
▼
Expected Results
count
6
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select count(*) from cd.facilities where guestcost >= 10;
This one is only a simple modification to the previous question: we need to weed out the inexpensive facilities.  This is easy to do using a
WHERE
clause. Our aggregation can now only see the expensive facilities.
Previous Exercise
/
/
Count2
Next Exercise
You'll need to add a
WHERE
clause to the answer of the previous question.
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
