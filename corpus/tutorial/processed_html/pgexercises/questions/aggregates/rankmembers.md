---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/aggregates/rankmembers.html"
source_url: "https://pgexercises.com/questions/aggregates/rankmembers.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Rank members by (rounded) hours used
Question
Produce a list of members (including guests), along with the number of hours they've booked in facilities, rounded to the nearest ten hours.  Rank them by this rounded figure, producing output of first name, surname, rounded hours, rank.  Sort by rank, surname, and first name.
Schema reminder
▼
Expected Results
firstname
surname
hours
rank
GUEST
GUEST
1200
1
Darren
Smith
340
2
Tim
Rownam
330
3
Tim
Boothe
220
4
Tracy
Smith
220
4
Gerald
Butters
210
6
Burton
Tracy
180
7
Charles
Owen
170
8
Janice
Joplette
160
9
Anne
Baker
150
10
Timothy
Baker
150
10
David
Jones
150
10
Nancy
Dare
130
13
Florence
Bader
120
14
Anna
Mackenzie
120
14
Ponder
Stibbons
120
14
Jack
Smith
110
17
Jemima
Farrell
90
18
David
Pinker
80
19
Ramnaresh
Sarwin
80
19
Matthew
Genting
70
21
Joan
Coplin
50
22
David
Farrell
30
23
Henry
Worthington-Smyth
30
23
John
Hunt
20
25
Douglas
Jones
20
25
Millicent
Purview
20
25
Henrietta
Rumney
20
25
Erica
Crumpet
10
29
Hyacinth
Tupperware
10
29
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select firstname, surname,
((sum(bks.slots)+10)/20)*10 as hours,
rank() over (order by ((sum(bks.slots)+10)/20)*10 desc) as rank

from cd.bookings bks
inner join cd.members mems
on bks.memid = mems.memid
group by mems.memid
order by rank, surname, firstname;
This answer isn't a great stretch over our previous exercise, although it does illustrate the function of
RANK
better.  You can see that some of the clubgoers have an equal rounded number of hours booked in, and their rank is the same.  If position 2 is shared between two members, the next one along gets position 4.  There's a different function,
DENSE_RANK
, that would assign that member position 3 instead.
It's worth noting the technique we use to do rounding here.  Adding 5, dividing by 10, and multiplying by 10 has the effect (thanks to integer arithmetic cutting off fractions) of rounding a number to the nearest 10.  In our case, because slots are half an hour, we need to add 10, divide by 20, and multiply by 10.  One could certainly make the argument that we should do the slots -> hours conversion independently of the rounding, which would increase clarity.
Talking of clarity, this rounding malarky is starting to introduce a noticeable amount of code repetition.  At this point it's a judgement call, but you may wish to factor it out using a subquery as below:
select firstname, surname, hours, rank() over (order by hours desc) from
(select firstname, surname,
((sum(bks.slots)+10)/20)*10 as hours

from cd.bookings bks
inner join cd.members mems
on bks.memid = mems.memid
group by mems.memid
) as subq
order by rank, surname, firstname;
Previous Exercise
/
/
Rankmembers
Next Exercise
You'll need the
RANK
window function again.  You can use integer arithmetic to accomplish rounding.
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
