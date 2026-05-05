---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/threejoin2.html"
source_url: "https://pgexercises.com/questions/joins/threejoin2.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

Produce a list of costly bookings
Question
How can you produce a list of bookings on the day of 2012-09-14 which will cost the member (or guest) more than $30?  Remember that guests have different costs to members (the listed costs are per half-hour 'slot'), and the guest user is always ID 0.  Include in your output the name of the facility, the name of the member formatted as a single column, and the cost.  Order by descending cost, and do not use any subqueries.
Schema reminder
▼
Expected Results
member
facility
cost
GUEST GUEST
Massage Room 2
320
GUEST GUEST
Massage Room 1
160
GUEST GUEST
Massage Room 1
160
GUEST GUEST
Massage Room 1
160
GUEST GUEST
Tennis Court 2
150
Jemima Farrell
Massage Room 1
140
GUEST GUEST
Tennis Court 1
75
GUEST GUEST
Tennis Court 2
75
GUEST GUEST
Tennis Court 1
75
Matthew Genting
Massage Room 1
70
Florence Bader
Massage Room 2
70
GUEST GUEST
Squash Court
70.0
Jemima Farrell
Massage Room 1
70
Ponder Stibbons
Massage Room 1
70
Burton Tracy
Massage Room 1
70
Jack Smith
Massage Room 1
70
GUEST GUEST
Squash Court
35.0
GUEST GUEST
Squash Court
35.0
Your Answer
Hint
Help
Save
Run Query
Answers and Discussion
Show
select mems.firstname || ' ' || mems.surname as member,
facs.name as facility,
case
when mems.memid = 0 then
bks.slots*facs.guestcost
else
bks.slots*facs.membercost
end as cost
from
cd.members mems
inner join cd.bookings bks
on mems.memid = bks.memid
inner join cd.facilities facs
on bks.facid = facs.facid
where
bks.starttime >= '2012-09-14' and
bks.starttime < '2012-09-15' and (
(mems.memid = 0 and bks.slots*facs.guestcost > 30) or
(mems.memid != 0 and bks.slots*facs.membercost > 30)
)
order by cost desc;
This is a bit of a complicated one!  While its more complex logic than we've used previously, there's not an awful lot to remark upon.  The
WHERE
clause restricts our output to sufficiently costly rows on 2012-09-14, remembering to distinguish between guests and others.  We then use a
CASE
statement in the column selections to output the correct cost for the member or guest.
Previous Exercise
/
Joins
/
Threejoin2
Next Exercise
As before, this answer requires multiple joins.  It's more complex
WHERE
logic than you're used to, and will require a
CASE
statement in the column selections!
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
