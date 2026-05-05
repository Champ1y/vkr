---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/agg2.html"
source_url: "https://pgexercises.com/questions/basic/agg2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Next Category
More aggregation
Question
You'd like to get the first and last name of the last member(s) who signed up - not just the date.  How can you do that?
Schema reminder
▼
Expected Results
firstname
surname
joindate
Darren
Smith
2012-09-26 18:08:45
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select firstname, surname, joindate
from cd.members
where joindate =
(select max(joindate)
from cd.members);
In the suggested approach above, you use a
subquery
to find out what the most recent joindate is.  This subquery returns a
scalar
table - that is, a table with a single column and a single row.  Since we have just a single value, we can substitute the subquery anywhere we might put a single constant value.  In this case, we use it to complete the
WHERE
clause of a query to find a given member.
You might hope that you'd be able to do something like below:
select firstname, surname, max(joindate)
from cd.members
Unfortunately, this doesn't work.  The
MAX
function doesn't restrict rows like the
WHERE
clause does - it simply takes in a bunch of values and returns the biggest one.  The database is then left wondering how to pair up a long list of names with the single join date that's come out of the max function, and fails.  Instead, you're left having to say 'find me the row(s) which have a join date that's the same as the maximum join date'.
As mentioned by the hint, there's other ways to get this job done - one example is below.  In this approach, rather than explicitly finding out what the last joined date is, we simply order our members table in descending order of join date, and pick off the first one.  Note that this approach does not cover the extremely unlikely eventuality of two people joining at the exact same time :-).
select firstname, surname, joindate
from cd.members
order by joindate desc
limit 1;
Previous Exercise
/
/
Agg2
Next Category
You may find you need a subquery to get this done - although other methods exist!
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
