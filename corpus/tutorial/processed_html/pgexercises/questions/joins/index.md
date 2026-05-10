---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/joins/index.html"
source_url: "https://pgexercises.com/questions/joins/index.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial. Факты должны подтверждаться official corpus выбранной версии."
---

Begin!
This category deals primarily with a foundational concept in relational database systems: joining.  Joining allows you to combine related information from multiple tables to answer a question.  This isn't just beneficial for ease of querying: a lack of join capability encourages denormalisation of data, which increases the complexity of keeping your data internally consistent.
This topic covers inner, outer, and self joins, as well as spending a little time on subqueries (queries within queries). If you struggle with these questions, I strongly recommend
Learning SQL
, by Alan Beaulieu, as a concise and well-written book on the subject.
Retrieve the start times of members' bookings
Work out the start times of bookings for tennis courts
Produce a list of all members who have recommended another member
Produce a list of all members, along with their recommender
Produce a list of all members who have used a tennis court
Produce a list of costly bookings
Produce a list of all members, along with their recommender, using no joins.
Produce a list of costly bookings, using a subquery
