"""Apply corporate events to the effective state used for evaluation.

This module never decides compliance. It only changes the data that the
rules read, and then the same rules run again.
"""

import copy


HOLDING_FIELD_EVENTS = {
    "DELISTING": "listing_status",
    "RATING_DOWNGRADE": "rating",
}

POLICY_EVENTS = {
    "FUND_REMOVED_FROM_APPROVED_LIST": "approved_funds",
}

OUT_OF_SCOPE_REASONS = {
    "DIVIDEND": "A dividend does not change any input used by rules R1-R5",
}


def classify_event(event):
    """Decide whether an event is relevant, and why."""
    event_type = str(event.get("event_type", "")).strip().upper()

    if event_type in HOLDING_FIELD_EVENTS:
        return True, f"Changes {HOLDING_FIELD_EVENTS[event_type]}, which is used by the rules"
    if event_type in POLICY_EVENTS:
        return True, "Changes the approved fund list, which is used by rule R3"

    reason = OUT_OF_SCOPE_REASONS.get(
        event_type, "Event type does not change any input used by rules R1-R5"
    )
    return False, reason


def apply_events(holdings, policy, events):
    """Return effective holdings, effective policy, and a record of each event.

    The inputs are never changed. Everything is applied to copies.
    """
    effective_holdings = copy.deepcopy(holdings)
    effective_policy = copy.deepcopy(policy)
    processed = []

    for event in events:
        event_type = str(event.get("event_type", "")).strip().upper()
        isin = str(event.get("isin", "")).strip().upper()
        new_value = str(event.get("new_value", "")).strip()

        relevant, reason = classify_event(event)
        affected = []

        if relevant and event_type in HOLDING_FIELD_EVENTS:
            field = HOLDING_FIELD_EVENTS[event_type]
            for holding in effective_holdings:
                if str(holding.get("isin", "")).strip().upper() == isin:
                    holding[field] = new_value
                    affected.append(holding.get("account_id", ""))

        elif relevant and event_type in POLICY_EVENTS:
            before = effective_policy["approved_funds"]
            effective_policy["approved_funds"] = [
                f for f in before
                if str(f["isin"]).strip().upper() != isin
            ]
            for holding in effective_holdings:
                if str(holding.get("isin", "")).strip().upper() == isin:
                    affected.append(holding.get("account_id", ""))

        processed.append({
            "event_id": event.get("event_id", ""),
            "event_type": event_type,
            "isin": isin,
            "relevant": relevant,
            "reason": reason,
            "applied_change": (
                f"{HOLDING_FIELD_EVENTS[event_type]} set to {new_value!r}"
                if relevant and event_type in HOLDING_FIELD_EVENTS
                else "removed from the approved fund list"
                if relevant and event_type in POLICY_EVENTS
                else "no change applied"
            ),
            "affected_accounts": affected,
        })

    return effective_holdings, effective_policy, processed