---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/date.html"
source_url: "https://pgexercises.com/questions/basic/date.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Working with dates
Question
How can you produce a list of members who joined after the start of September 2012?
Return the memid, surname, firstname, and joindate of the members in question.
Schema reminder
▼
Expected Results
memid
surname
firstname
joindate
24
Sarwin
Ramnaresh
2012-09-01 08:44:42
26
Jones
Douglas
2012-09-02 18:43:05
27
Rumney
Henrietta
2012-09-05 08:42:35
28
Farrell
David
2012-09-15 08:22:05
29
Worthington-Smyth
Henry
2012-09-17 12:27:15
30
Purview
Millicent
2012-09-18 19:04:01
33
Tupperware
Hyacinth
2012-09-18 19:32:05
35
Hunt
John
2012-09-19 11:32:45
36
Crumpet
Erica
2012-09-22 08:36:38
37
Smith
Darren
2012-09-26 18:08:45
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select memid, surname, firstname, joindate
from cd.members
where joindate >= '2012-09-01';
This is our first look at SQL timestamps.  They're formatted in descending order of magnitude:
YYYY-MM-DD HH:MM:SS.nnnnnn
.  We can compare them just like we might a unix timestamp, although getting the differences between dates is a little more involved (and powerful!).  In this case, we've just specified the date portion of the timestamp.  This gets automatically cast by postgres into the full timestamp
2012-09-01 00:00:00
.
Previous Exercise
/
/
Next Exercise
Look up the SQL timestamp format, and remember that you can compare dates much like you would integer values.
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
