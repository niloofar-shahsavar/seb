import json
from app.rules import evaluate_holding

policy = json.load(open("policy/rules.json"))
policy.update(json.load(open("policy/approved_venues.json")))
policy.update(json.load(open("policy/approved_funds.json")))

new_holdings = [
    {"isin": "SE0001000175", "name": "Sandvik AB", "asset_type": "equity", "issuer_group": "SAND", "rating": "", "exchange": "XSTO", "listing_status": "listed"},
    {"isin": "SE0001000183", "name": "Nordic Real Return Fund", "asset_type": "fund", "issuer_group": "NORDFUND", "rating": "", "exchange": "", "listing_status": "n/a"},
    {"isin": "SE0001000191", "name": "Baltic Logistics 2029", "asset_type": "bond", "issuer_group": "BALTLOG", "rating": "BB", "exchange": "XSTO", "listing_status": "listed"},
    {"isin": "KY0001000203", "name": "Cayman Absolute Return", "asset_type": "fund", "issuer_group": "CAYMAN", "rating": "", "exchange": "", "listing_status": "n/a"},
    {"isin": "SE0001000217", "name": "Hallands Vind 2032", "asset_type": "bond", "issuer_group": "HALLVIND", "rating": "NR", "exchange": "XSTO", "listing_status": "listed"},
    {"isin": "SE0001000225", "name": "Autocall Nordic 6Y", "asset_type": "structured_product", "issuer_group": "NORDBANK", "rating": "", "exchange": "XSTO", "listing_status": "listed"},
    {"isin": "SE0001000233", "name": "SEB A", "asset_type": "equity", "issuer_group": "SEB", "rating": "", "exchange": "XSTO", "listing_status": "listed"},
    {"isin": "SE0001000241", "name": "Sylvan Bioscience AB", "asset_type": "equity", "issuer_group": "SYLVAN", "rating": "", "exchange": "", "listing_status": "unlisted"},
]

expected = ["APPROVED", "APPROVED", "REJECTED", "REJECTED", "REVIEW", "REJECTED", "REJECTED", "REJECTED"]

for h, exp in zip(new_holdings, expected):
    a = evaluate_holding(h, policy)
    mark = "OK " if a["status"] == exp else "XX "
    cause = [r.rule_id for r in a["rule_results"] if r.status in ("FAIL", "REVIEW")]
    print(f"{mark}{h['name']:26} {a['status']:9} expected {exp:9} caused by {cause}")