"""Read CSV and JSON files and normalise them into plain Python data.

No compliance logic here - this module only reads and shapes data.
All paths are anchored to the backend folder, so the loaders work no
matter which directory the program is started from.
"""

import glob
import json
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
POLICY_DIR = BACKEND_DIR / "policy"


def load_policy(policy_dir=POLICY_DIR):
    """Merge the three policy JSON files into one dict."""
    policy_dir = Path(policy_dir)

    policy = json.loads((policy_dir / "rules.json").read_text())
    policy.update(json.loads((policy_dir / "approved_venues.json").read_text()))
    policy.update(json.loads((policy_dir / "approved_funds.json").read_text()))

    # Fail fast: a minimum rating outside the scale would make R4 unusable.
    if policy["minimum_rating"] not in policy["rating_scale"]:
        raise ValueError(
            f"minimum_rating {policy['minimum_rating']!r} is not in rating_scale"
        )

    return policy


def load_holdings_file(path):
    """Read one holdings snapshot into a list of dicts."""
    rows = _read_csv(path)
    for row in rows:
        row["market_value"] = _to_number(row.get("market_value"))
        row["quantity"] = _to_number(row.get("quantity"))
    return rows


def load_all_holdings(data_dir=DATA_DIR):
    """Load every holdings snapshot, keyed by date, oldest first."""
    snapshots = {}
    for path in sorted(glob.glob(str(Path(data_dir) / "holdings_*.csv"))):
        rows = load_holdings_file(path)
        if rows:
            snapshots[rows[0]["date"]] = rows
    return snapshots


def load_corporate_events(path=DATA_DIR / "corporate_events.csv"):
    """Read the corporate events file into a list of dicts."""
    return _read_csv(path)


def _read_csv(path):
    """Read a CSV into a list of dicts. Every value stays a stripped string."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().lower() for c in df.columns]

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