---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/updates/insert2.html"
source_url: "https://pgexercises.com/questions/updates/insert2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Insert multiple rows of data into a table
Question
In the previous exercise, you learned how to add a facility. Now you're going to add multiple facilities in one command. Use the following values:
facid: 9, Name: 'Spa', membercost: 20, guestcost: 30, initialoutlay: 100000, monthlymaintenance: 800.
facid: 10, Name: 'Squash Court 2', membercost: 3.5, guestcost: 17.5, initialoutlay: 5000, monthlymaintenance: 80.
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
2
Badminton Court
0
15.5
4000
50
3
Table Tennis
0
5
320
10
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
7
Snooker Table
0
5
450
15
8
Pool Table
0
5
400
15
9
Spa
20
30
100000
800
10
Squash Court 2
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
insert into cd.facilities
(facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
values
(9, 'Spa', 20, 30, 100000, 800),
(10, 'Squash Court 2', 3.5, 17.5, 5000, 80);
VALUES
can be used to generate more than one row to insert into a table, as seen in this example. Hopefully it's clear what's going on here: the output of
VALUES
is a table, and that table is copied into cd.facilities, the table specified in the
INSERT
command.
While you'll most commonly see
VALUES
when inserting data, Postgres allows you to use
VALUES
wherever you might use a
SELECT
. This makes sense: the output of both commands is a table, it's just that
VALUES
is a bit more ergonomic when working with constant data.
Similarly, it's possible to use
SELECT
wherever you see a
VALUES
. This means that you can
INSERT
the results of a
SELECT
. For example:
insert into cd.facilities
(facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
SELECT 9, 'Spa', 20, 30, 100000, 800
UNION ALL
SELECT 10, 'Squash Court 2', 3.5, 17.5, 5000, 80;
In later exercises you'll see us using
INSERT ... SELECT
to generate data to insert based on the information already in the database.
Previous Exercise
/
Updates
/
Insert2
Next Exercise
VALUES
can be used to generate more than one row.
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
