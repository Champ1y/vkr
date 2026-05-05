---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/nummembers.html"
source_url: "https://pgexercises.com/questions/aggregates/nummembers.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a numbered list of members
Question
Produce a monotonically increasing numbered list of members (including guests), ordered by their date of joining.  Remember that member IDs are not guaranteed to be sequential.
Schema reminder
▼
Expected Results
row_number
firstname
surname
1
GUEST
GUEST
2
Darren
Smith
3
Tracy
Smith
4
Tim
Rownam
5
Janice
Joplette
6
Gerald
Butters
7
Burton
Tracy
8
Nancy
Dare
9
Tim
Boothe
10
Ponder
Stibbons
11
Charles
Owen
12
David
Jones
13
Anne
Baker
14
Jemima
Farrell
15
Jack
Smith
16
Florence
Bader
17
Timothy
Baker
18
David
Pinker
19
Matthew
Genting
20
Anna
Mackenzie
21
Joan
Coplin
22
Ramnaresh
Sarwin
23
Douglas
Jones
24
Henrietta
Rumney
25
David
Farrell
26
Henry
Worthington-Smyth
27
Millicent
Purview
28
Hyacinth
Tupperware
29
John
Hunt
30
Erica
Crumpet
31
Darren
Smith
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select row_number() over(order by joindate), firstname, surname
from cd.members
order by joindate
This exercise is a simple bit of window function practise!  You could just as easily use
count(*) over(order by joindate)
here, so don't worry if you used that instead.
In this query, we don't define a partition, meaning that the partition is the entire dataset.  Since we define an order for the window function, for any given row the window is: start of the dataset -> current row.
Previous Exercise
/
/
Nummembers
Next Exercise
Read up on the
ROW_NUMBER
window function.
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
