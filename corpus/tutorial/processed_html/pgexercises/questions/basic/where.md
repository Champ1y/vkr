---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/where.html"
source_url: "https://pgexercises.com/questions/basic/where.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Control which rows are retrieved
Question
How can you produce a list of facilities that charge a fee to members?
Schema reminder
▼
Expected Results
facid
name
membercost
guestcost
initialoutlay
monthlymaintenance
0
Tennis Court 1
5
25
10000
200
1
Tennis Court 2
5
25
8000
200
4
Massage Room 1
35
80
4000
3000
5
Massage Room 2
35
80
4000
3000
6
Squash Court
3.5
17.5
5000
80
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select * from cd.facilities where membercost > 0;
The
FROM
clause is used to build up a set of candidate rows to read results from.  In our examples so far, this set of rows has simply been the contents of a table.  In future we will explore joining, which allows us to create much more interesting candidates.
Once we've built up our set of candidate rows, the
WHERE
clause allows us to filter for the rows we're interested in - in this case, those with a membercost of more than zero.  As you will see in later exercises,
WHERE
clauses can have multiple components combined with boolean logic - it's possible to, for instance, search for facilities with a cost greater than 0 and less than 10.  The filtering action of the
WHERE
clause on the facilities table is illustrated below:
Previous Exercise
/
/
Where
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
