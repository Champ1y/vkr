---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/daysremaining.html"
source_url: "https://pgexercises.com/questions/date/daysremaining.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Work out the number of days remaining in the month
Question
For any given timestamp, work out the number of days remaining in the month.  The current day should count as a whole day, regardless of the time.  Use '2012-02-11 01:00:00' as an example timestamp for the purposes of making the answer.  Format the output as a single interval value.
Schema reminder
▼
Expected Results
remaining
19 days
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select (date_trunc('month',ts.testts) + interval '1 month')
- date_trunc('day', ts.testts) as remaining
from (select timestamp '2012-02-11 01:00:00' as testts) ts
The star of this particular show is the
DATE_TRUNC
function.  It does pretty much what you'd expect - truncates a date to a given minute, hour, day, month, and so on.  The way we've solved this problem is to truncate our timestamp to find the month we're in, add a month to that, and subtract our timestamp.  To ensure partial days get treated as whole days, the timestamp we subtract is truncated to the nearest day.
Note the way we've put the timestamp into a subquery.  This isn't required, but it does mean you can give the timestamp a name, rather than having to list the literal repeatedly.
Previous Exercise
/
/
Daysremaining
Next Exercise
Take a look at the
DATE_TRUNC
function
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
