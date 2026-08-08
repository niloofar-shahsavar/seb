### Dependency issue
1. I encountered a dependency conflict while setting up the frontend. I resolved it by using a compatible package version and committing `package-lock.json` to keep the dependency versions consistent across environments.

AI suggested possible fixes, but I confirmed the solution by testing the project locally.


2. I asked an AI model to read my two holdings files and my corporate events file and explain what the data actually contained, instead of only trusting my own description of it. I checked the row and ISIN counts myself and confirmed that the 8 new ISINs matched the 8 test cases I had planned. The review found three things I had not thought through: all my fund rows have an empty exchange and listing_status = n/a, so my listing rule has to return NOT_APPLICABLE for funds or every fund would fail; all my equity rows have an empty rating, so my rating rule has to return NOT_APPLICABLE for equities or every equity would end up as REVIEW; and my fund-removal event changes a policy file rather than a holdings column, so it is a different kind of change from a delisting or a downgrade. It also pointed out that the note column in my events file contains the answer in plain text, and that my code must decide relevance from the event type instead of reading that column. I agreed with all of these and will handle them when I write the rules.

3. 