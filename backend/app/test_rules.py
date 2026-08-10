from app.loaders import load_policy, load_all_holdings, load_corporate_events

policy = load_policy("policy")
print("minimum rating:", policy["minimum_rating"])
print("approved funds:", len(policy["approved_funds"]))
print("approved venues:", len(policy["approved_venues"]))

snapshots = load_all_holdings("data")
for date, rows in snapshots.items():
    isins = {r["isin"] for r in rows}
    print(date, "->", len(rows), "rows,", len(isins), "unique ISINs")

events = load_corporate_events("data/corporate_events.csv")
for e in events:
    print(e["event_id"], e["event_type"], e["isin"])


from app.events import apply_events
from app.rules import evaluate_holding

eff_holdings, eff_policy, processed = apply_events(
    snapshots["2026-08-04"], policy, events
)

print("\n--- event classification ---")
for p in processed:
    print(f"{p['event_id']} {p['event_type']:35} relevant={p['relevant']} accounts={p['affected_accounts']}")

print("\n--- before events ---")
before = 0
for h in snapshots["2026-08-04"]:
    a = evaluate_holding(h, policy)
    if a["status"] != "APPROVED":
        before += 1
        print(f"  {a['status']:9} {h['name']}")
print("  total:", before)

print("\n--- after events ---")
after = 0
for h in eff_holdings:
    a = evaluate_holding(h, eff_policy)
    if a["status"] != "APPROVED":
        after += 1
        rules = [r.rule_id for r in a["rule_results"] if r.status in ("FAIL", "REVIEW")]
        print(f"  {a['status']:9} {h['account_id']} {h['name']:30} {rules}")
print("  total:", after)

from app.alerts import build_alerts, sort_alerts

all_alerts = []
for h in eff_holdings:
    a = evaluate_holding(h, eff_policy)
    all_alerts.extend(build_alerts(a))

print("\n--- alerts:", len(all_alerts), "---")
for al in sort_alerts(all_alerts)[:4]:
    print(f"{al['severity']:7} {al['rule_id']} {al['name']:30} {al['observed_field']}={al['observed_value']!r} -> {al['suggested_action']}")