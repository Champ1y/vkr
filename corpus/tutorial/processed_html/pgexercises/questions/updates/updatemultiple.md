---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/updates/updatemultiple.html"
source_url: "https://pgexercises.com/questions/updates/updatemultiple.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Update multiple rows and columns at the same time
Question
We want to increase the price of the tennis courts for both members and guests. Update the costs to be 6 for members, and 30 for guests.
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
6
30
10000
200
1
Tennis Court 2
6
30
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
update cd.facilities
set
membercost = 6,
guestcost = 30
where facid in (0,1);
The
SET
clause accepts a comma separated list of values that you want to update.
Previous Exercise
/
Updates
/
Updatemultiple
Next Exercise
The
SET
clause can update multiple columns.
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
