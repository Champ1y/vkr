---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/reg.html"
source_url: "https://pgexercises.com/questions/string/reg.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Find telephone numbers with parentheses
Question
You've noticed that the club's member table has telephone numbers with very inconsistent formatting.  You'd like to find all the telephone numbers that contain parentheses, returning the member ID and telephone number sorted by member ID.
Schema reminder
▼
Expected Results
memid
telephone
0
(000) 000-0000
3
(844) 693-0723
4
(833) 942-4710
5
(844) 078-4130
6
(822) 354-9973
7
(833) 776-4001
8
(811) 433-2547
9
(833) 160-3900
10
(855) 542-5251
11
(844) 536-8036
13
(855) 016-0163
14
(822) 163-3254
15
(833) 499-3527
20
(811) 972-1377
21
(822) 661-2898
22
(822) 499-2232
24
(822) 413-1470
27
(822) 989-8876
28
(855) 755-9876
29
(855) 894-3758
30
(855) 941-9786
33
(822) 665-5327
35
(899) 720-6978
36
(811) 732-4816
37
(822) 577-3541
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select memid, telephone from cd.members where telephone ~ '[()]';
We've chosen to answer this using regular expressions, although Postgres does provide other string functions like
POSITION
that would do the job at least as well.  Postgres implements POSIX regular expression matching via the
~
operator. If you've used regular expressions before, the functionality of the operator will be very familiar to you.
As an alternative, you can use the SQL standard
SIMILAR TO
operator.  The regular expressions for this have similarities to the POSIX standard, but a lot of differences as well. Some of the most notable differences are:
As in the
LIKE
operator,
SIMILAR TO
uses the '_' character to mean 'any character', and the '%' character to mean 'any string'.
A
SIMILAR TO
expression must match the whole string, not just a substring as in posix regular expressions.  This means that you'll typically end up bracketing an expression in '%' characters.
The '.' character does not mean 'any character' in
SIMILAR TO
regexes: it's just a plain character.
The
SIMILAR TO
equivalent of the given answer is shown below:
select memid, telephone from cd.members where telephone similar to '%[()]%';
Finally, it's worth noting that regular expressions usually don't use indexes.  Generally you don't want your regex to be responsible for doing heavy lifting in your query, because it will be slow.  If you need fuzzy matching that works fast, consider working out if your needs can be met by
full text search
.
Previous Exercise
/
/
Reg
Next Exercise
Look up the ~ or
SIMILAR TO
operators in the Postgres docs.
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
