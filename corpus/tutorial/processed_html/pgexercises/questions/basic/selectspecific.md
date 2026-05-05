---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/basic/selectspecific.html"
source_url: "https://pgexercises.com/questions/basic/selectspecific.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Retrieve specific columns from a table
Question
You want to print out a list of all of the facilities and their cost to members.  How would you retrieve a list of only facility names and costs?
Schema reminder
▼
Expected Results
name
membercost
Tennis Court 1
5
Tennis Court 2
5
Badminton Court
0
Table Tennis
0
Massage Room 1
35
Massage Room 2
35
Squash Court
3.5
Snooker Table
0
Pool Table
0
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select name, membercost from cd.facilities;
For this question, we need to specify the columns that we want.  We can do that with a simple comma-delimited list of column names specified to the select statement.  All the database does is look at the columns available in the
FROM
clause, and return the ones we asked for, as illustrated below
Generally speaking, for non-throwaway queries it's considered desirable to specify the names of the columns you want in your queries rather than using *.  This is because your application might not be able to cope if more columns get added into the table.
Previous Exercise
/
/
Selectspecific
Next Exercise
The select statement allows you to specify column names to retrieve.
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
