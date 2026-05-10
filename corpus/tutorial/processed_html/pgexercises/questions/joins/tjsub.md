---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/tjsub.html"
source_url: "https://pgexercises.com/questions/joins/tjsub.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Next Category
Produce a list of costly bookings, using a subquery
Question
The
Produce a list of costly bookings
exercise contained some messy logic: we had to calculate the booking cost in both the
WHERE
clause and the
CASE
statement.  Try to simplify this calculation using subqueries.  For reference, the question was:
How can you produce a list of bookings on the day of 2012-09-14 which will cost the member (or guest) more than $30?  Remember that guests have different costs to members (the listed costs are per half-hour 'slot'), and the guest user is always ID 0.  Include in your output the name of the facility, the name of the member formatted as a single column, and the cost.  Order by descending cost.
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
select member, facility, cost from (
select
mems.firstname || ' ' || mems.surname as member,
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
bks.starttime < '2012-09-15'
) as bookings
where cost > 30
order by cost desc;
This answer provides a mild simplification to the previous iteration: in the no-subquery version, we had to calculate the member or guest's cost in both the
WHERE
clause and the
CASE
statement.  In our new version, we produce an inline query that calculates the total booking cost for us, allowing the outer query to simply select the bookings it's looking for.  For reference, you may also see subqueries in the
FROM
clause referred to as
inline views
.
Previous Exercise
/
Joins
/
Tjsub
Next Category
Your answer will be similar to the referenced exercise.  Use a subquery in the
FROM
clause to generate a result set that calculates the total cost of each booking.  The outer query can then select the bookings it's interested in.
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
