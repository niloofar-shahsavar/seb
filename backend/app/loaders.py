import glob
import json
import os

import pandas as pd


def load_policy(policy_dir="policy"):
    """Merge the three policy JSON files into one dict."""
    policy = json.load(open(os.path.join(policy_dir, "rules.json")))
    policy.update(json.load(open(os.path.join(policy_dir, "approved_venues.json"))))
    policy.update(json.load(open(os.path.join(policy_dir, "approved_funds.json"))))

    
    if policy["minimum_rating"] not in policy["rating_scale"]:
        raise ValueError(
            f"minimum_rating {policy['minimum_rating']!r} is not in rating_scale"
        )

    return policy


def load_holdings_file(path):
    """Read one holdings snapshot into a list of dicts."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]

    rows = df.to_dict("records")
    for row in rows:
        for key in row:
            row[key] = str(row[key]).strip()
        row["market_value"] = _to_number(row.get("market_value"))
        row["quantity"] = _to_number(row.get("quantity"))
    return rows


def load_all_holdings(data_dir="data"):
    """Load every holdings snapshot, keyed by date, oldest first."""
    snapshots = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "holdings_*.csv"))):
        rows = load_holdings_file(path)
        if not rows:
            continue
        snapshots[rows[0]["date"]] = rows
    return snapshots


def load_corporate_events(path):
    """Read the corporate events file into a list of dicts."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]

    rows = df.to_dict("records")
    for row in rows:
        for key in row:
            row[key] = str(row[key]).strip()
    return rows


def _to_number(value):
    """Convert a numeric string to float, or return 0.0 if it cannot be read."""
    try:
        return float(str(value).replace(" ", ""))
    except (TypeError, ValueError):
        return 0.0