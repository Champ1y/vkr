---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/fachours2.html"
source_url: "https://pgexercises.com/questions/aggregates/fachours2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Output the facility id that has the highest number of slots booked
Question
Output the facility id that has the highest number of slots booked. For bonus points, try a version without a
LIMIT
clause.  This version will probably look messy!
Schema reminder
▼
Expected Results
facid
Total Slots
4
1404
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, sum(slots) as "Total Slots"
from cd.bookings
group by facid
order by sum(slots) desc
LIMIT 1;
Let's start off with what's arguably the simplest way to do this: produce a list of facility IDs and the total number of slots used, order by the total number of slots used, and pick only the top result.
It's worth realising, though, that this method has a significant weakness.  In the event of a tie, we will still only get one result!  To get all the relevant results, we might try using the
MAX
aggregate function, something like below:
select facid, max(totalslots) from (
select facid, sum(slots) as totalslots
from cd.bookings
group by facid
) as sub group by facid
The intent of this query is to get the highest totalslots value and its associated facid(s).  Unfortunately, this just won't work!  In the event of multiple facids having the same number of slots booked, it would be ambiguous which facid should be paired up with the single (or
scalar
) value coming out of the
MAX
function.  This means that Postgres will tell you that facid ought to be in a
GROUP BY
section, which won't produce the results we're looking for.
Let's take a first stab at a working query:
select facid, sum(slots) as totalslots
from cd.bookings
group by facid
having sum(slots) = (select max(sum2.totalslots) from
(select sum(slots) as totalslots
from cd.bookings
group by facid
) as sum2);
The query produces a list of facility IDs and number of slots used, and then uses a
HAVING
clause that works out the maximum totalslots value.  We're essentially saying: 'produce a list of facids and their number of slots booked, and filter out all the ones that doen't have a number of slots booked equal to the maximum.'
Useful as
HAVING
is, however, our query is pretty ugly.  To improve on that, let's introduce another new concept:
Common Table Expressions
(CTEs).  CTEs can be thought of as allowing you to define a database view inline in your query.  It's really helpful in situations like this, where you're having to repeat yourself a lot.
CTEs are declared in the form
WITH CTEName as (SQL-Expression)
.  You can see our query redefined to use a CTE below:
with sum as (select facid, sum(slots) as totalslots
from cd.bookings
group by facid
)
select facid, totalslots
from sum
where totalslots = (select max(totalslots) from sum);
You can see that we've factored out our repeated selections from cd.bookings into a single CTE, and made the query a lot simpler to read in the process!
BUT WAIT.  There's more.  It's also possible to complete this problem using Window Functions.  We'll leave these until later, but even better solutions to problems like these are available.
That's a lot of information for a single exercise.  Don't worry too much if you don't get it all right now - we'll reuse these concepts in later exercises.
Previous Exercise
/
/
Fachours2
Next Exercise
Consider the use of the
LIMIT
keyword combined with
ORDER BY
.  For the
LIMIT
-less version, you'll probably want to investigate the
HAVING
keyword.  Be aware that the latter version is difficult!
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
