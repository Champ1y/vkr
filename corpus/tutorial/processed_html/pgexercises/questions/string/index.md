---
title: "PostgreSQL exercises"
language: "en"
corpus_type: "supplementary"
source_role: "external_exercise"
source_format: "html_cleaned_to_markdown"
original_html_path: "html/pgexercises/questions/string/index.html"
source_url: "https://pgexercises.com/questions/string/index.html"
indexable: true
usage_rule: "Использовать только как supplementary слой в tutorial + extended_mode. Факты должны подтверждаться official corpus выбранной версии."
---

String Operations
Begin!
String operations in most RDBMSs are, arguably, needlessly painful.  Fortunately, Postgres is better than most in this regard, providing strong regular expression support.  This section covers basic string manipulation, use of the LIKE operator, and use of regular expressions.  I also make an effort to show you some alternative approaches that work reliably in most RDBMSs.  Be sure to check out Postgres' string function
docs page
if you're not confident about these exercises.
Anthony Molinaro's
SQL Cookbook
provides some excellent documentation of (difficult) cross-DBMS compliant SQL string manipulation.  I'd strongly recommend his book.
Format the names of members
Find facilities by a name prefix
Perform a case-insensitive search
Find telephone numbers with parentheses
Pad zip codes with leading zeroes
Count the number of members whose surname starts with each letter of the alphabet
Clean up telephone numbers
