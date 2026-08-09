AI Usage
Dependency issue

I had a dependency conflict while setting up the frontend. AI suggested some possible solutions, and I fixed it by using a compatible package version. I tested the solution locally and committed package-lock.json so the same versions are used in other environments.

Data review

I asked AI to review my holdings and corporate events files and explain what the data contained. I checked the row counts and ISINs myself and confirmed that the 8 new ISINs matched my 8 planned test cases.

The review showed me some important cases I had missed. Funds should not be checked by the listing rule, because all my fund rows have an empty exchange and a listing status of n/a. Equities should not be checked by the rating rule, because all my equity rows have an empty rating. And some corporate events change policy data instead of holdings data, so they have to be handled differently.

I also noticed that the note column in my events file explains in plain text why each event matters. My code does not read that column and decides relevance from the event type instead, because otherwise my rules would just be copying the answer out of my own test data.

Policy and rules

I used AI to help decide what should be stored in JSON and what should stay in Python. I checked the suggested policy values against my own data and made sure they supported my test cases correctly.

I decided to keep rule settings, such as the rating scale and approved funds, in JSON and keep the rule logic in Python. I also added a policy version so results can show which version of the policy was used.

AI also helped me write and review the rule functions. I made several decisions myself, such as keeping pandas out of the rules, passing holdings as simple dictionaries, and checking important boundary cases like BBB- passing while BB+ fails. For external facts such as the investment grade boundary, I checked a rating agency source instead of only trusting AI.

During one design discussion an AI suggested removing the NOT_APPLICABLE results to keep the output smaller. A second review pointed out that this would remove the proof that a rule actually ran. I agreed and kept all rule results, so I can always see the difference between a rule that did not apply and a rule that never ran.

I tested all five rules against my 8 new holdings and confirmed that each result matched the test case I had planned.

Data loading

I used AI to help with the loading functions and understand the pandas settings. I learned that reading the CSV data as text is important, because pandas would otherwise turn empty ratings into NaN and could remove the leading zeros from my ISINs, which would break my fund lookups.

I kept pandas only in the loading part of the project and converted the data to dictionaries before passing it to the rules. I also added validation for the policy configuration so an invalid setting causes a clear error instead of silently producing incorrect results.

Finally, I checked the loaded row counts and unique ISIN counts against my own manual counts to confirm that the data was loaded correctly.

Limitations

Most AI suggestions were reasonable but too general for my data. The real problems only appeared when I compared a suggestion to my actual CSV files. AI also cannot confirm facts about the outside world, such as where the investment grade boundary sits, so I checked that against a rating agency source.