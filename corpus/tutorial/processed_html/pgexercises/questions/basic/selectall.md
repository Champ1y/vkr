---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/selectall.html"
source_url: "https://pgexercises.com/questions/basic/selectall.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Question
How can you retrieve all the information from the cd.facilities table?
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
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select * from cd.facilities;
The
SELECT
statement is the basic starting block for queries that read information out of the database.  A minimal select statement is generally comprised of
select [some set of columns] from [some table or group of tables]
.
In this case, we want all of the information from the facilities table.  The
from
section is easy - we just need to specify the
cd.facilities
table.  'cd' is the table's schema - a term used for a logical grouping of related information in the database.
Next, we need to specify that we want all the columns.  Conveniently, there's a shorthand for 'all columns' -
*
.  We can use this instead of laboriously specifying all the column names.
/
/
Selectall
Next Exercise
select *
can be used to retrieve all columns from a table.
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
