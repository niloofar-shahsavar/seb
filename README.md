# Portfolio Bond Compliance Monitoring

A prototype monitoring tool for a Portfolio Bond (Swedish `depåförsäkring`). The customer chooses the investments, but the insurance company owns the assets, so it has to make sure every holding follows its investment policy.

## What it does

Two scenarios from the case, implemented end to end:

1. **New investment detected, then eligibility check**
2. **Corporate event, then revalidation**

Portfolio level rules, such as a limit on one issuer, are out of scope. They need to add up several holdings, which is a different type of rule from the per holding rules here.

## The data

Synthetic files in `backend/data/`.

| File | Rows | Unique ISINs |
| --- | --- | --- |
| holdings_2026-08-03.csv | 20 | 16 |
| holdings_2026-08-04.csv | 26 | 22 |

A snapshot shows what each account held at the end of one day. It is not a list of what was bought. I need two days because "new" is a comparison, so one snapshot on its own cannot tell me what is new.

`corporate_events.csv` has four events. Three change something the rules use, one does not.

## Monitoring rules

**A holding is new** when its ISIN has never appeared in any account on any earlier day. I detect newness per ISIN and not per account, because eligibility depends on the instrument and the policy, not on which customer bought it.

**The daily run has two passes.** Pass 1 finds new ISINs. Pass 2 revalidates every holding, new and old. The second pass is what makes this continuous monitoring instead of only a purchase checker, because something that was fine yesterday can become non compliant today without anyone buying anything.

**The five policy rules:**

| Rule | Checks | Applies to |
| --- | --- | --- |
| R1 | Asset type is equity, fund or bond | all |
| R2 | Listed and on an approved venue | equities, bonds |
| R3 | Fund is on the approved fund list | funds |
| R4 | Bond rating is BBB- or better | bonds |
| R5 | Issuer is not in the insurer's own group | all |

**Each rule returns** PASS, FAIL, REVIEW or NOT_APPLICABLE. Any FAIL makes the holding REJECTED. No FAIL but a REVIEW makes it REVIEW. Otherwise APPROVED. NOT_APPLICABLE never changes the status and never creates an alert, but I keep it anyway so I can see the difference between a rule that stood down and a rule that never ran.

**FAIL and REVIEW are not the same.** FAIL is a statement about the holding, REVIEW is a statement about my data. An equity marked `unlisted` fails R2 because the data tells me it is not listed. An equity with an empty listing status returns REVIEW, because a gap in my feed should not become an accusation against the asset.

## Corporate events

An event matters if and only if it changes an input used by one of R1 to R5.

| Event | Type | Changes | Relevant |
| --- | --- | --- | --- |
| EVT001 | Delisting | listing status | Yes, R2 |
| EVT002 | Rating downgrade | rating, BBB- to BB+ | Yes, R4 |
| EVT003 | Fund removed from approved list | the approved fund set | Yes, R3 |
| EVT004 | Dividend | nothing a rule reads | No |

The dividend is still loaded and reported with the reason it was ignored. If it disappeared silently I could not tell the difference between correctly out of scope and a parser bug.

My event file has a `note` column that explains each event in plain text. My code does not read it. Relevance comes from the event type through a mapping in `events.py`, because otherwise my engine would be copying the answer out of my own test data.

Events never decide compliance. They change the data, and then the same five rules run again. Nothing is written back to my CSV or JSON files, so running the same data twice gives the same result.

## Alerts

Only FAIL and REVIEW create alerts. Each one says which rule found it, which field and value caused it, what the policy expected, and what a person should do about it. Suggested actions are recommendations, never automatic decisions.

Each alert records whether it came from a new holding or a corporate event. The rule result is the same, but a new holding that fails is a purchase to block while an existing one is a remediation case.

Alerts are sorted with breaches first and then by largest position. Market value affects ordering only, never the decision.

## Results for 2026-08-04

| Metric | Value |
| --- | --- |
| Holdings | 26 |
| New ISINs | 8 |
| Approved / Review / Rejected | 16 / 1 / 9 |
| Alerts | 10 |
| Events applied / ignored | 3 / 1 |

The eight new holdings, each chosen to test one rule:

| Holding | Result | Reason |
| --- | --- | --- |
| Sandvik AB | APPROVED | permitted listed equity |
| Nordic Real Return Fund | APPROVED | fund is approved |
| Baltic Logistics 2029 | REJECTED | R4, rating BB |
| Cayman Absolute Return | REJECTED | R3, fund not approved |
| Hallands Vind 2032 | REVIEW | R4, no usable rating |
| Autocall Nordic 6Y | REJECTED | R1, structured product |
| SEB A | REJECTED | R5, own group issuer |
| Sylvan Bioscience AB | REJECTED | R2, not listed |

I wrote these down before implementing anything, so they check my code rather than describe it.

Before the events are applied, 6 holdings are not approved and all 6 are new. After the events, 10 are. The four extra are Nordwind Marine in two accounts (delisted), Saltsjo Property (downgraded) and Frontier Emerging Opportunities (fund removed). Nobody bought anything to cause them, and I wrote no new compliance logic to find them. The same five rules ran again against changed data.

## How it is built

**Policy configuration.** Rule settings live in three JSON files under `policy/`, rule logic lives in Python. A compliance officer can add an approved venue or fund without touching code. I did not make the rules themselves configurable, because that would turn my JSON into a small programming language. The rating scale is an ordered list, so R4 compares two positions in that list instead of comparing text, which would give alphabetical order rather than credit quality order.

**Rules.** Each rule takes one holding as a plain dictionary and returns a result object holding the rule id, the status, the field it looked at, the value it found, what was expected and a short reason. The alert text is built from those fields, which is why an alert can explain itself.

R2, R3 and R4 check the asset type first. This matters in my data: every fund row has an empty exchange, so without that check every fund would fail the listing rule, and every equity row has an empty rating, so every equity would end up as REVIEW.

All five rules are combined in one shared `evaluate_holding()`. New investments, event affected holdings and daily monitoring all use it, so the same holding always gets the same result from the same data and policy.

**Loaders.** The only part that reads files. Everything is read as text so empty cells stay empty instead of becoming NaN and ISINs keep their leading zeros. Each row becomes a plain dictionary, so my rules never see a dataframe. The policy loader stops with an error if the minimum rating is not in the rating scale, because a typo there would either fail every bond or pass every bond, and the second one would be invisible.

**Pipeline.** Coordinates the daily run and packages the result. It contains no compliance logic.

**API.** `GET /api/daily-run` returns the whole run. `main.py` calls the pipeline and returns the result.

**Dashboard.** One screen: summary tiles, new holdings, corporate events including the ignored dividend, and the alerts table. Uses the SEB Green colour tokens and typeface.

## Assumptions

1. One end of day snapshot per business day, assumed complete
2. Holdings are positions, not transactions
3. One simplified rating scale
4. Reference data comes from local synthetic files
5. Rules are evaluated per holding
6. Concentration rules are out of scope
7. Past results are not rewritten when something changes today
8. Market values are SEK
9. Quantity and market value are not used by any rule, only to sort alerts

## Known limitations

**Adding a new asset type needs a code change.** If `structured_product` were added to the permitted list, R1 would pass it but R2, R3 and R4 would all return NOT_APPLICABLE, so it could be approved with no listing or rating check. Every asset type should be explicitly mapped to the rules that apply to it. The configuration split is safe for making the policy stricter but not for widening it.

**A re bought instrument is not new again.** Mitigated by the daily revalidation pass.

**Events are applied without checking the old value** matches what the holding currently has.

## Running the project

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Backend on port 8000, frontend on 5173. CORS allows the frontend port.

I could not create a virtual environment with `python3 -m venv` on my machine because `ensurepip` was failing, so I used `uv` instead. `requirements.txt` is a normal pip file and works with the commands above.

## Structure

```
backend/app/
├── main.py       FastAPI endpoints
├── loaders.py    read CSV and JSON
├── rules.py      R1 to R5 and evaluate_holding
├── events.py     apply corporate events
├── alerts.py     findings to alerts
└── pipeline.py   coordinate the daily run
```

No database, repository classes or dependency injection. The data is three CSV files and three JSON files, and those layers would have made the project harder to explain without making it work better.

## AI usage

See [AI_USAGE.md](AI_USAGE.md).