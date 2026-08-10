# AI Usage

## Dependency issue

I had a dependency conflict while setting up the frontend, between `@sebgroup/green-react` and `@sebgroup/green-core`. AI suggested some possible solutions, and I fixed it by pinning green-core to a compatible version. I tested the solution locally and committed `package-lock.json` so the same versions are used in other environments.

## Data review

I asked AI to review my holdings and corporate events files and explain what the data contained, instead of only trusting my own description of it. I checked the row counts and ISINs myself and confirmed that the 8 new ISINs matched my 8 planned test cases.

The review showed me some important cases I had missed. Funds should not be checked by the listing rule, because all my fund rows have an empty exchange and a listing status of n/a. Equities should not be checked by the rating rule, because all my equity rows have an empty rating. Without those checks, every fund would have failed and every equity would have ended up as REVIEW. It also pointed out that some corporate events change policy data instead of holdings data, so they have to be handled differently.

I also noticed that the `note` column in my events file explains in plain text why each event matters. My code does not read that column and decides relevance from the event type instead, because otherwise my rules would just be copying the answer out of my own test data.

## Policy and rules

I used AI to help decide what should be stored in JSON and what should stay in Python. I checked the suggested policy values against my own data and made sure they supported my test cases correctly. That is how I found that the fund my removal event targets has to be on the approved list from the start, and that the Cayman fund has to be missing from it, otherwise two of my test cases would pass for the wrong reason.

I decided to keep rule settings, such as the rating scale and the approved funds, in JSON and keep the rule logic in Python. I also added a policy version so a result can show which version of the policy it was judged against.

AI also helped me write and review the rule functions. I made several decisions myself, such as keeping pandas out of the rules, passing holdings as simple dictionaries, and checking important boundary cases like BBB- passing while BB+ fails. For external facts such as where the investment grade boundary sits, I checked a rating agency source instead of only trusting AI.

One useful suggestion I kept was a branch that returns REVIEW when a rating is not in my scale at all, so that one unexpected value cannot stop the whole daily run.

During one design discussion an AI suggested removing the NOT_APPLICABLE results to keep the output smaller. A second review pointed out that this would remove the proof that a rule actually ran. I agreed and kept all rule results, so I can always see the difference between a rule that did not apply and a rule that never ran.

I tested all five rules against my 8 new holdings and confirmed that each result matched the test case I had planned.

## Data loading

I used AI to help with the loading functions and to understand the pandas settings I needed. Reading the CSV data as text matters, because pandas would otherwise turn empty ratings into NaN and could remove the leading zeros from my ISINs, which would break my fund lookups.

I kept pandas only in the loading part of the project and converted the data to dictionaries before passing it to the rules. This also avoids the clash between the pandas `.isin()` method and my column called `isin`, because after loading there is no dataframe left anywhere.

I added validation for the policy configuration so that an invalid setting causes a clear error instead of silently producing incorrect results. I thought through the alternatives first: a broken minimum rating could either fail every bond, which is wrong but obvious, or pass every bond, which is wrong and invisible on a dashboard. Stopping the run is the safer option.

Finally, I checked the loaded row counts and unique ISIN counts against my own manual counts to confirm that the data was loaded correctly.

## Events, alerts and the pipeline

I used AI to help structure the corporate event handling. The design decision I kept throughout is that event code never decides compliance. It only changes the effective data, on in memory copies, and then the same five rules run again. I verified this by counting the non compliant holdings before and after the events: 6 before and 10 after, with the four extra ones being exactly the instruments my three relevant events target.

I checked the whole daily run against numbers I had worked out from the data beforehand, including that the dividend is recorded as out of scope rather than silently dropped.

## Environment problem

I could not create a Python virtual environment on my machine, because `ensurepip` and then pip itself kept failing. AI helped me read the error, which turned out to be a pip bug where an empty macOS version string crashes one of its internal libraries. Several suggested fixes did not work, including pinning an older pip, because the installer itself uses the broken version. Installing `uv` and creating the environment with it solved it. I noted this in the README so a reviewer knows why the setup instructions mention it.

## Limitations

Most AI suggestions were reasonable but too general for my data. The real problems only appeared when I compared a suggestion to my actual CSV files, which is why I checked the data myself before implementing anything.

AI also cannot confirm facts about the outside world, such as where the investment grade boundary sits, so I checked that against a rating agency source.

Suggestions were sometimes more complicated than my prototype needed, and I turned some of them down to keep the project small enough that I can explain every part of it.