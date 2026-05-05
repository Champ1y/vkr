---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/where2.html"
source_url: "https://pgexercises.com/questions/basic/where2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Control which rows are retrieved - part 2
Question
How can you produce a list of facilities that charge a fee to members, and that fee is less than 1/50th of the monthly maintenance cost?  Return the facid, facility name, member cost, and monthly maintenance of the facilities in question.
Schema reminder
▼
Expected Results
facid
name
membercost
monthlymaintenance
4
Massage Room 1
35
3000
5
Massage Room 2
35
3000
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select facid, name, membercost, monthlymaintenance
from cd.facilities
where
membercost > 0 and
(membercost < monthlymaintenance/50.0);
The
WHERE
clause allows us to filter for the rows we're interested in - in this case, those with a membercost of more than zero, and less than 1/50th of the monthly maintenance cost.  As you can see, the massage rooms are very expensive to run thanks to staffing costs!
When we want to test for two or more conditions, we use
AND
to combine them.  We can, as you might expect, use
OR
to test whether either of a pair of conditions is true.
You might have noticed that this is our first query that combines a
WHERE
clause with selecting specific columns.  You can see in the image below the effect of this: the intersection of the selected columns and the selected rows gives us the data to return.  This may not seem too interesting now, but as we add in more complex operations like joins later, you'll see the simple elegance of this behaviour.
Previous Exercise
/
/
Where2
Next Exercise
The
WHERE
clause allows you to filter the rows that you want to retrieve.
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
