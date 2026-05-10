---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/updates/deletewh.html"
source_url: "https://pgexercises.com/questions/updates/deletewh.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Delete a member from the cd.members table
Question
We want to remove member 37, who has never made a booking, from our database. How can we achieve that?
Schema reminder
▼
Expected Results
memid
surname
firstname
address
zipcode
telephone
recommendedby
joindate
0
GUEST
GUEST
GUEST
0
(000) 000-0000
2012-07-01 00:00:00
1
Smith
Darren
8 Bloomsbury Close, Boston
4321
555-555-5555
2012-07-02 12:02:05
2
Smith
Tracy
8 Bloomsbury Close, New York
4321
555-555-5555
2012-07-02 12:08:23
3
Rownam
Tim
23 Highway Way, Boston
23423
(844) 693-0723
2012-07-03 09:32:15
4
Joplette
Janice
20 Crossing Road, New York
234
(833) 942-4710
1
2012-07-03 10:25:05
5
Butters
Gerald
1065 Huntingdon Avenue, Boston
56754
(844) 078-4130
1
2012-07-09 10:44:09
6
Tracy
Burton
3 Tunisia Drive, Boston
45678
(822) 354-9973
2012-07-15 08:52:55
7
Dare
Nancy
6 Hunting Lodge Way, Boston
10383
(833) 776-4001
4
2012-07-25 08:59:12
8
Boothe
Tim
3 Bloomsbury Close, Reading, 00234
234
(811) 433-2547
3
2012-07-25 16:02:35
9
Stibbons
Ponder
5 Dragons Way, Winchester
87630
(833) 160-3900
6
2012-07-25 17:09:05
10
Owen
Charles
52 Cheshire Grove, Winchester, 28563
28563
(855) 542-5251
1
2012-08-03 19:42:37
11
Jones
David
976 Gnats Close, Reading
33862
(844) 536-8036
4
2012-08-06 16:32:55
12
Baker
Anne
55 Powdery Street, Boston
80743
844-076-5141
9
2012-08-10 14:23:22
13
Farrell
Jemima
103 Firth Avenue, North Reading
57392
(855) 016-0163
2012-08-10 14:28:01
14
Smith
Jack
252 Binkington Way, Boston
69302
(822) 163-3254
1
2012-08-10 16:22:05
15
Bader
Florence
264 Ursula Drive, Westford
84923
(833) 499-3527
9
2012-08-10 17:52:03
16
Baker
Timothy
329 James Street, Reading
58393
833-941-0824
13
2012-08-15 10:34:25
17
Pinker
David
5 Impreza Road, Boston
65332
811 409-6734
13
2012-08-16 11:32:47
20
Genting
Matthew
4 Nunnington Place, Wingfield, Boston
52365
(811) 972-1377
5
2012-08-19 14:55:55
21
Mackenzie
Anna
64 Perkington Lane, Reading
64577
(822) 661-2898
1
2012-08-26 09:32:05
22
Coplin
Joan
85 Bard Street, Bloomington, Boston
43533
(822) 499-2232
16
2012-08-29 08:32:41
24
Sarwin
Ramnaresh
12 Bullington Lane, Boston
65464
(822) 413-1470
15
2012-09-01 08:44:42
26
Jones
Douglas
976 Gnats Close, Reading
11986
844 536-8036
11
2012-09-02 18:43:05
27
Rumney
Henrietta
3 Burkington Plaza, Boston
78533
(822) 989-8876
20
2012-09-05 08:42:35
28
Farrell
David
437 Granite Farm Road, Westford
43532
(855) 755-9876
2012-09-15 08:22:05
29
Worthington-Smyth
Henry
55 Jagbi Way, North Reading
97676
(855) 894-3758
2
2012-09-17 12:27:15
30
Purview
Millicent
641 Drudgery Close, Burnington, Boston
34232
(855) 941-9786
2
2012-09-18 19:04:01
33
Tupperware
Hyacinth
33 Cheerful Plaza, Drake Road, Westford
68666
(822) 665-5327
2012-09-18 19:32:05
35
Hunt
John
5 Bullington Lane, Boston
54333
(899) 720-6978
30
2012-09-19 11:32:45
36
Crumpet
Erica
Crimson Road, North Reading
75655
(811) 732-4816
2
2012-09-22 08:36:38
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
delete from cd.members where memid = 37;
This exercise is a small increment on our previous one. Instead of deleting all bookings, this time we want to be a bit more targeted, and delete a single member that has never made a booking. To do this, we simply have to add a
WHERE
clause to our command, specifying the member we want to delete. You can see the parallels with
SELECT
and
UPDATE
statements here.
There's one interesting wrinkle here. Try this command out, but substituting in member id 0 instead. This member has made many bookings, and you'll find that the delete fails with an error about a foreign key constraint violation. This is an important concept in relational databases, so let's explore a little further.
Foreign keys are a mechanism for defining relationships between columns of different tables. In our case we use them to specify that the memid column of the bookings table is related to the memid column of the members table. The relationship (or 'constraint') specifies that for a given booking, the member specified in the booking
must
exist in the members table. It's useful to have this guarantee enforced by the database: it means that code using the database can rely on the presence of the member. It's hard (even impossible) to enforce this at higher levels: concurrent operations can interfere and leave your database in a broken state.
PostgreSQL supports various different kinds of constraints that allow you to enforce structure upon your data. For more information on constraints, check out the PostgreSQL documentation on
foreign keys
Previous Exercise
Home
/
Updates
/
Deletewh
Next Exercise
Take a look at the
DELETE
statement in the PostgreSQL docs.
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
