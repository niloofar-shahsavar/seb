import json
from app.pipeline import run_daily_monitoring

result = run_daily_monitoring()

print("run date:", result["run_date"])
print("policy:", result["policy_version"])
print("new ISINs:", len(result["new_isins"]))
print("summary:", json.dumps(result["summary"], indent=2))

print("\nevents:")
for e in result["corporate_events"]:
    print(f"  {e['event_id']} {e['event_type']:35} relevant={e['relevant']}")

print("\ntop alerts:")
for a in result["alerts"][:5]:
    print(f"  {a['severity']:7} {a['rule_id']} {a['name']:30} {a['trigger']}")

json.dumps(result)
print("\nJSON serialisation: ok")