---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/date/endtimes.html"
source_url: "https://pgexercises.com/questions/date/endtimes.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Work out the end time of bookings
Question
Return a list of the start and end time of the last 10 bookings (ordered by the time at which they end, followed by the time at which they start) in the system.
Schema reminder
▼
Expected Results
starttime
endtime
2013-01-01 15:30:00
2013-01-01 16:00:00
2012-09-30 19:30:00
2012-09-30 20:30:00
2012-09-30 19:00:00
2012-09-30 20:30:00
2012-09-30 19:30:00
2012-09-30 20:00:00
2012-09-30 19:00:00
2012-09-30 20:00:00
2012-09-30 19:00:00
2012-09-30 20:00:00
2012-09-30 18:30:00
2012-09-30 20:00:00
2012-09-30 18:30:00
2012-09-30 20:00:00
2012-09-30 19:00:00
2012-09-30 19:30:00
2012-09-30 18:30:00
2012-09-30 19:30:00
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select starttime, starttime + slots*(interval '30 minutes') endtime
from cd.bookings
order by endtime desc, starttime desc
limit 10
This question simply returns the start time for a booking, and a calculated end time which is equal to
start time + (30 minutes * slots)
.  Note that it's perfectly okay to multiply intervals.
The other thing you'll notice is the use of order by and limit to get the last ten bookings.  All this does is order the bookings by the (descending) time at which they end, and pick off the top ten.
Previous Exercise
/
/
Endtimes
Next Exercise
You can multiply an interval by the number of slots in a booking.
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
