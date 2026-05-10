---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/pad.html"
source_url: "https://pgexercises.com/questions/string/pad.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Pad zip codes with leading zeroes
Question
The zip codes in our example dataset have had leading zeroes removed from them by virtue of being stored as a numeric type.  Retrieve all zip codes from the members table, padding any zip codes less than 5 characters long with leading zeroes.  Order by the new zip code.
Schema reminder
▼
Expected Results
zip
00000
00234
00234
04321
04321
10383
11986
23423
28563
33862
34232
43532
43533
45678
52365
54333
56754
57392
58393
64577
65332
65464
66796
68666
69302
75655
78533
80743
84923
87630
97676
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select lpad(cast(zipcode as char(5)),5,'0') zip from cd.members order by zip
Postgres'
LPAD
function is the star of this particular show. It does basically what you'd expect: allow us to produce a padded string.  We need to remember to cast the zipcode to a string for it to be accepted by the
LPAD
function.
When inheriting an old database, It's not that unusual to find wonky decisions having been made over data types.  You may wish to fix mistakes like these, but have a lot of code that would break if you changed datatypes.  In that case, one option (depending on performance requirements) is to create a
view
over your table which presents the data in a fixed-up manner, and gradually migrate.
Previous Exercise
/
/
Pad
Next Exercise
Check out the
LPAD
function.  You'll also need to cast the zipcode column to a character string.
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
