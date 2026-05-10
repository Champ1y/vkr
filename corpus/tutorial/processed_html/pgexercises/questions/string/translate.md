---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/translate.html"
source_url: "https://pgexercises.com/questions/string/translate.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Next Category
Clean up telephone numbers
Question
The telephone numbers in the database are very inconsistently formatted.  You'd like to print a list of member ids and numbers that have had '-','(',')', and ' ' characters removed.  Order by member id.
Schema reminder
▼
Expected Results
memid
telephone
0
0000000000
1
5555555555
2
5555555555
3
8446930723
4
8339424710
5
8440784130
6
8223549973
7
8337764001
8
8114332547
9
8331603900
10
8555425251
11
8445368036
12
8440765141
13
8550160163
14
8221633254
15
8334993527
16
8339410824
17
8114096734
20
8119721377
21
8226612898
22
8224992232
24
8224131470
26
8445368036
27
8229898876
28
8557559876
29
8558943758
30
8559419786
33
8226655327
35
8997206978
36
8117324816
37
8225773541
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select memid, translate(telephone, '-() ', '') as telephone
from cd.members
order by memid;
The most direct solution is probably the
TRANSLATE
function, which can be used to replace characters in a string.  You pass it three strings: the value you want altered, the characters to replace, and the characters you want them replaced with.  In our case, we want all the characters deleted, so our third parameter is an empty string.
As is often the way with strings, we can also use regular expressions to solve our problem.  The
REGEXP_REPLACE
function provides what we're looking for: we simply pass a regex that matches all non-digit characters, and replace them with nothing, as shown below.  The 'g' flag tells the function to replace as many instances of the pattern as it can find.  This solution is perhaps more robust, as it cleans out more bad formatting.
select memid, regexp_replace(telephone, '[^0-9]', '', 'g') as telephone
from cd.members
order by memid;
Making automated use of free-formatted text data can be a chore.  Ideally you want to avoid having to constantly write code to clean up the data before using it, so you should consider having your database enforce correct formatting for you. You can do this using a
CHECK
constraint on your column, which allow you to reject any poorly-formatted entry.  It's tempting to perform this kind of validation in the application layer, and this is certainly a valid approach.  As a general rule, if your database is getting used by multiple applications, favour pushing more of your checks down into the database to ensure consistent behaviour between the apps.
Occasionally, adding a constraint isn't feasible.  You may, for example, have two different legacy applications asserting differently formatted information.  If you're unable to alter the applications, you have a couple of options to consider.  Firstly, you can define a
trigger
on your table.  This allows you to intercept data before (or after) it gets asserted to your table, and normalise it into a single format.  Alternatively, you could build a
view
over your table that cleans up information on the fly, as it's read out.  Newer applications can read from the view and benefit from more reliably formatted information.
Previous Exercise
/
/
Translate
Next Category
Consider the
TRANSLATE
or
REGEXP_REPLACE
functions.
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
