"""Turn compliance findings into actionable alerts.

Only FAIL and REVIEW create alerts. PASS and NOT_APPLICABLE do not.
"""

# Suggested actions are operational recommendations, not automatic decisions.
SUGGESTED_ACTIONS = {
    ("R1", "FAIL"): "Block purchase and escalate to Compliance",
    ("R2", "FAIL"): "Initiate remediation review and assess exit options",
    ("R2", "REVIEW"): "Obtain listing status from reference data",
    ("R3", "FAIL"): "Submit fund for approval or initiate remediation review",
    ("R3", "REVIEW"): "Obtain fund identifier from reference data",
    ("R4", "FAIL"): "Initiate remediation review and assess exit options",
    ("R4", "REVIEW"): "Obtain missing credit rating",
    ("R5", "FAIL"): "Block purchase and escalate to Compliance",
    ("R1", "REVIEW"): "Obtain asset classification from reference data",
    ("R5", "REVIEW"): "Obtain issuer group from reference data",
}

DEFAULT_ACTIONS = {
    "FAIL": "Escalate to Compliance",
    "REVIEW": "Obtain missing data and re-evaluate",
}


def build_alerts(assessment, is_new=False, event_ids=None):
    """Create one alert for each FAIL or REVIEW rule result in one assessment."""
    alerts = []

    for result in assessment["rule_results"]:
        if result.status not in ("FAIL", "REVIEW"):
            continue

        action = SUGGESTED_ACTIONS.get(
            (result.rule_id, result.status), DEFAULT_ACTIONS[result.status]
        )

        alerts.append({
            "account_id": assessment["account_id"],
            "isin": assessment["isin"],
            "name": assessment["name"],
            "market_value": assessment["market_value"],
            "holding_status": assessment["status"],
            "severity": result.status,
            "rule_id": result.rule_id,
            "rule_name": result.rule_name,
            "observed_field": result.observed_field,
            "observed_value": result.observed_value,
            "expected": result.expected,
            "reason": result.reason,
            "suggested_action": action,
            "trigger": "new_holding" if is_new else ("corporate_event" if event_ids else "daily_revalidation"),
            "event_ids": event_ids or [],
        })

    return alerts


def sort_alerts(alerts):
    """FAIL before REVIEW, then largest exposure first."""
    return sorted(
        alerts,
        key=lambda a: (0 if a["severity"] == "FAIL" else 1, -a["market_value"]),
    )