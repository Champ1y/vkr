---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/updates/insert.html"
source_url: "https://pgexercises.com/questions/updates/insert.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Question
The club is adding a new facility - a spa. We need to add it into the facilities table. Use the following values:
facid: 9, Name: 'Spa', membercost: 20, guestcost: 30, initialoutlay: 100000, monthlymaintenance: 800.
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
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
insert into cd.facilities
(facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
values (9, 'Spa', 20, 30, 100000, 800);
INSERT INTO ... VALUES
is the simplest way to insert data into a table. There's not a whole lot to discuss here:
VALUES
is used to construct a row of data, which the
INSERT
statement inserts into the table. It's a simple as that.
You can see that there's two sections in parentheses. The first is part of the
INSERT
statement, and specifies the columns that we're providing data for. The second is part of
VALUES
, and specifies the actual data we want to insert into each column.
If we're inserting data into every column of the table, as in this example, explicitly specifying the column names is optional. As long as you fill in data for all columns of the table, in the order they were defined when you created the table, you can do something like the following:
insert into cd.facilities values (9, 'Spa', 20, 30, 100000, 800);
Generally speaking, for SQL that's going to be reused I tend to prefer being explicit and specifying the column names.
/
Updates
/
Insert
Next Exercise
INSERT
can be used to insert data into a table.
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
