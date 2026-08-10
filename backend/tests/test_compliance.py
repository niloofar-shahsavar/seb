"""Tests for the compliance rules and the daily monitoring run."""

from app.pipeline import run_daily_monitoring
from app.rules import check_r4, evaluate_holding
from app.loaders import load_policy

RUN = run_daily_monitoring("2026-08-04")
POLICY = load_policy()

EXPECTED_NEW = {
    "Sandvik AB": "APPROVED",
    "Nordic Real Return Fund": "APPROVED",
    "Baltic Logistics 2029": "REJECTED",
    "Cayman Absolute Return": "REJECTED",
    "Hallands Vind 2032": "REVIEW",
    "Autocall Nordic 6Y": "REJECTED",
    "SEB A": "REJECTED",
    "Sylvan Bioscience AB": "REJECTED",
}


def test_eight_new_holdings_have_expected_status():
    new_holdings = {h["name"]: h["status"] for h in RUN["holdings"] if h["is_new"]}
    assert new_holdings == EXPECTED_NEW


def test_relevant_events_are_applied_and_dividend_is_ignored():
    by_id = {e["event_id"]: e for e in RUN["corporate_events"]}
    assert by_id["EVT001"]["relevant"] is True
    assert by_id["EVT002"]["relevant"] is True
    assert by_id["EVT003"]["relevant"] is True
    assert by_id["EVT004"]["relevant"] is False
    assert by_id["EVT004"]["affected_accounts"] == []


def test_events_make_previously_compliant_holdings_non_compliant():
    failing = {
        (h["account_id"], h["name"])
        for h in RUN["holdings"]
        if h["status"] != "APPROVED" and not h["is_new"]
    }
    assert failing == {
        ("ACC002", "Nordwind Marine AB"),
        ("ACC005", "Nordwind Marine AB"),
        ("ACC004", "Saltsjo Property 2028"),
        ("ACC004", "Frontier Emerging Opportunities"),
    }


def test_rating_boundary_is_inclusive():
    at_minimum = {"asset_type": "bond", "rating": "BBB-"}
    one_notch_below = {"asset_type": "bond", "rating": "BB+"}
    assert check_r4(at_minimum, POLICY).status == "PASS"
    assert check_r4(one_notch_below, POLICY).status == "FAIL"


def test_not_applicable_results_are_kept():
    equity = {
        "account_id": "X", "isin": "SE0001000019", "name": "Volvo B",
        "asset_type": "equity", "issuer_group": "VOLVO", "rating": "",
        "exchange": "XSTO", "listing_status": "listed", "market_value": 100,
    }
    assessment = evaluate_holding(equity, POLICY)

    assert len(assessment["rule_results"]) == 5
    statuses = {r.rule_id: r.status for r in assessment["rule_results"]}
    assert statuses["R3"] == "NOT_APPLICABLE"
    assert statuses["R4"] == "NOT_APPLICABLE"
    assert assessment["status"] == "APPROVED"


def test_only_fail_and_review_create_alerts():
    severities = {a["severity"] for a in RUN["alerts"]}
    assert severities <= {"FAIL", "REVIEW"}
    assert len(RUN["alerts"]) == 10