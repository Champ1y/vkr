---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/agg.html"
source_url: "https://pgexercises.com/questions/basic/agg.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Simple aggregation
Question
You'd like to get the signup date of your last member.  How can you retrieve this information?
Schema reminder
▼
Expected Results
latest
2012-09-26 18:08:45
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select max(joindate) as latest
from cd.members;
This is our first foray into SQL's aggregate functions.  They're used to extract information about whole groups of rows, and allow us to easily ask questions like:
What's the most expensive facility to maintain on a monthly basis?
Who has recommended the most new members?
How much time has each member spent at our facilities?
The
MAX
aggregate function here is very simple: it receives all the possible values for joindate, and outputs the one that's biggest.  There's a lot more power to aggregate functions, which you will come across in future exercises.
Previous Exercise
/
/
Agg
Next Exercise
Look up the SQL aggregate function
MAX
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
