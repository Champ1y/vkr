---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/simplejoin.html"
source_url: "https://pgexercises.com/questions/joins/simplejoin.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Retrieve the start times of members' bookings
Question
How can you produce a list of the start times for bookings by members named 'David Farrell'?
Schema reminder
▼
Expected Results
starttime
2012-09-18 09:00:00
2012-09-18 17:30:00
2012-09-18 13:30:00
2012-09-18 20:00:00
2012-09-19 09:30:00
2012-09-19 15:00:00
2012-09-19 12:00:00
2012-09-20 15:30:00
2012-09-20 11:30:00
2012-09-20 14:00:00
2012-09-21 10:30:00
2012-09-21 14:00:00
2012-09-22 08:30:00
2012-09-22 17:00:00
2012-09-23 08:30:00
2012-09-23 17:30:00
2012-09-23 19:00:00
2012-09-24 08:00:00
2012-09-24 16:30:00
2012-09-24 12:30:00
2012-09-25 15:30:00
2012-09-25 17:00:00
2012-09-26 13:00:00
2012-09-26 17:00:00
2012-09-27 08:00:00
2012-09-28 11:30:00
2012-09-28 09:30:00
2012-09-28 13:00:00
2012-09-29 16:00:00
2012-09-29 10:30:00
2012-09-29 13:30:00
2012-09-29 14:30:00
2012-09-29 17:30:00
2012-09-30 14:30:00
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select bks.starttime
from
cd.bookings bks
inner join cd.members mems
on mems.memid = bks.memid
where
mems.firstname='David'
and mems.surname='Farrell';
The most commonly used kind of join is the
INNER JOIN
.  What this does is combine two tables based on a join expression - in this case, for each member id in the members table, we're looking for matching values in the bookings table.  Where we find a match, a row combining the values for each table is returned.  Note that we've given each table an
alias
(bks and mems).  This is used for two reasons: firstly, it's convenient, and secondly we might join to the same table several times, requiring us to distinguish between columns from each different time the table was joined in.
Let's ignore our select and where clauses for now, and focus on what the
FROM
statement produces.  In all our previous examples, FROM has just been a simple table.  What is it now?  Another table!  This time, it's produced as a composite of bookings and members.  You can see a subset of the output of the join below:
For each member in the members table, the join has found all the matching member ids in the bookings table.  For each match, it's then produced a row combining the row from the members table, and the row from the bookings table.
Obviously, this is too much information on its own, and any useful question will want to filter it down.  In our query, we use the start of the
SELECT
clause to pick columns, and the WHERE clause to pick rows, as illustrated below:
That's all we need to find David's bookings!  In general, I encourage you to remember that the output of the FROM clause is essentially one big table that you then filter information out of.  This may sound inefficient - but don't worry, under the covers the DB will be behaving much more intelligently :-).
One final note: there's two different syntaxes for inner joins.  I've shown you the one I prefer, that I find more consistent with other join types.  You'll commonly see a different syntax, shown below:
select bks.starttime
from
cd.bookings bks,
cd.members mems
where
mems.firstname='David'
and mems.surname='Farrell'
and mems.memid = bks.memid;
This is functionally exactly the same as the approved answer.  If you feel more comfortable with this syntax, feel free to use it!
/
Joins
/
Simplejoin
Next Exercise
Take a look at the documentation for
INNER JOIN
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
