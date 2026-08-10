"""Coordinate one daily monitoring run.

This module contains no compliance logic. It decides the order of the
steps and packages the result that the API returns.
"""

from app.alerts import build_alerts, sort_alerts
from app.events import apply_events
from app.loaders import load_all_holdings, load_corporate_events, load_policy
from app.rules import evaluate_holding


def find_new_isins(snapshots, run_date):
    """ISINs held on run_date that were never held on any earlier day."""
    seen_before = set()
    for date, holdings in snapshots.items():
        if date < run_date:
            for holding in holdings:
                seen_before.add(holding["isin"])

    today_isins = {h["isin"] for h in snapshots[run_date]}
    return sorted(today_isins - seen_before)


def run_daily_monitoring(run_date=None):
    """Run one full day of monitoring and return the complete result."""
    policy = load_policy()
    snapshots = load_all_holdings()
    events = load_corporate_events()

    if run_date is None:
        run_date = max(snapshots)
    if run_date not in snapshots:
        raise ValueError(f"No holdings snapshot found for {run_date}")

    # Pass 1 - what appeared for the first time. This does not decide compliance.
    new_isins = find_new_isins(snapshots, run_date)

    # Corporate events change the effective state only. Source files are untouched.
    todays_events = [e for e in events if e.get("date", run_date) == run_date]
    effective_holdings, effective_policy, processed_events = apply_events(
        snapshots[run_date], policy, todays_events
    )

    # Pass 2 - revalidate every holding, new and old, with the same rules.
    assessments = []
    alerts = []

    for holding in effective_holdings:
        assessment = evaluate_holding(holding, effective_policy)

        is_new = holding["isin"] in new_isins
        related_events = [
            e["event_id"]
            for e in processed_events
            if e["relevant"] and e["isin"] == holding["isin"]
        ]

        assessment["is_new"] = is_new
        assessment["related_event_ids"] = related_events

        # Build alerts first, while rule_results are still RuleResult objects.
        alerts.extend(
            build_alerts(assessment, is_new=is_new, event_ids=related_events)
        )

        # Then make the assessment JSON-friendly for the API response.
        assessment["rule_results"] = [vars(r) for r in assessment["rule_results"]]
        assessments.append(assessment)

    alerts = sort_alerts(alerts)

    return {
        "run_date": run_date,
        "policy_version": policy.get("policy_version", "unknown"),
        "new_isins": new_isins,
        "holdings": assessments,
        "alerts": alerts,
        "corporate_events": processed_events,
        "summary": {
            "total_holdings": len(assessments),
            "new_holdings": sum(1 for a in assessments if a["is_new"]),
            "approved": sum(1 for a in assessments if a["status"] == "APPROVED"),
            "review": sum(1 for a in assessments if a["status"] == "REVIEW"),
            "rejected": sum(1 for a in assessments if a["status"] == "REJECTED"),
            "alert_count": len(alerts),
            "events_applied": sum(1 for e in processed_events if e["relevant"]),
            "events_ignored": sum(1 for e in processed_events if not e["relevant"]),
        },
    }