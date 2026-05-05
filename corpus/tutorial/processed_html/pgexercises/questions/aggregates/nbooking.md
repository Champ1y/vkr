---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/nbooking.html"
source_url: "https://pgexercises.com/questions/aggregates/nbooking.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

List each member's first booking after September 1st 2012
Question
Produce a list of each member name, id, and their first booking after September 1st 2012.  Order by member ID.
Schema reminder
▼
Expected Results
surname
firstname
memid
starttime
GUEST
GUEST
0
2012-09-01 08:00:00
Smith
Darren
1
2012-09-01 09:00:00
Smith
Tracy
2
2012-09-01 11:30:00
Rownam
Tim
3
2012-09-01 16:00:00
Joplette
Janice
4
2012-09-01 15:00:00
Butters
Gerald
5
2012-09-02 12:30:00
Tracy
Burton
6
2012-09-01 15:00:00
Dare
Nancy
7
2012-09-01 12:30:00
Boothe
Tim
8
2012-09-01 08:30:00
Stibbons
Ponder
9
2012-09-01 11:00:00
Owen
Charles
10
2012-09-01 11:00:00
Jones
David
11
2012-09-01 09:30:00
Baker
Anne
12
2012-09-01 14:30:00
Farrell
Jemima
13
2012-09-01 09:30:00
Smith
Jack
14
2012-09-01 11:00:00
Bader
Florence
15
2012-09-01 10:30:00
Baker
Timothy
16
2012-09-01 15:00:00
Pinker
David
17
2012-09-01 08:30:00
Genting
Matthew
20
2012-09-01 18:00:00
Mackenzie
Anna
21
2012-09-01 08:30:00
Coplin
Joan
22
2012-09-02 11:30:00
Sarwin
Ramnaresh
24
2012-09-04 11:00:00
Jones
Douglas
26
2012-09-08 13:00:00
Rumney
Henrietta
27
2012-09-16 13:30:00
Farrell
David
28
2012-09-18 09:00:00
Worthington-Smyth
Henry
29
2012-09-19 09:30:00
Purview
Millicent
30
2012-09-19 11:30:00
Tupperware
Hyacinth
33
2012-09-20 08:00:00
Hunt
John
35
2012-09-23 14:00:00
Crumpet
Erica
36
2012-09-27 11:30:00
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select mems.surname, mems.firstname, mems.memid, min(bks.starttime) as starttime
from cd.bookings bks
inner join cd.members mems on
mems.memid = bks.memid
where starttime >= '2012-09-01'
group by mems.surname, mems.firstname, mems.memid
order by mems.memid;
This answer demonstrates the use of aggregate functions on dates.
MIN
works exactly as you'd expect, pulling out the lowest possible date in the result set.  To make this work, we need to ensure that the result set only contains dates from September onwards.  We do this using the
WHERE
clause.
You might typically use a query like this to find a customer's next booking.  You can use this by replacing the date '2012-09-01' with the function
now()
Previous Exercise
/
/
Nbooking
Next Exercise
Take a look at the
MIN
aggregate function
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
