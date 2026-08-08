I started by looking at the data I had already created before writing any code. I have two end-of-day holdings snapshots, one for 2026-08-03 and one for 2026-08-04, and one file with four corporate events. A snapshot shows what each account held on that date, not what was bought, so I need two days to be able to see what is new. I decided that a holding is new when its ISIN has not been seen in any account on any earlier day, because eligibility depends on the instrument and the policy and not on which customer bought it. When I compared the two files I found 8 new ISINs and 2 instruments that had been sold, which matched what I expected.


The policy has two parts that must be stored separately:

Settings — the values a compliance officer might change without a developer: which asset types are permitted, which venues are approved, which funds are approved, what the minimum rating is. These go in JSON.
Logic — how to compare a rating against a minimum, how to decide a rule doesn't apply. This goes in Python.
