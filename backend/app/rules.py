from dataclasses import dataclass

@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    status: str
    observed_field: str
    observed_value: str
    expected: str
    reason: str

#I used a dataclass because it keeps structured data,
# clear and makes field name mistakes easier to catch.

#r1

def check_r1(holding, policy):
    permitted = policy["permitted_asset_types"]
    expected = "one of: " + ", ".join(permitted)

    asset_type = str(holding.get("asset_type", "")).strip().lower()

    if asset_type == "":
        status = "REVIEW"
        reason = "Asset type is missing, so the rule cannot be evaluated"
    elif asset_type in permitted:
        status = "PASS"
        reason = "Asset type is permitted by the investment policy"
    else: 
        status = "FAIL"
        reason = "Asset type is not permitted by the investment policy"

    return RuleResult(
        rule_id="R1",
        rule_name="Permitted asset classes",
        status= status,
        observed_field="asset_type",
        observed_value=asset_type,
        expected=expected,
        reason=reason,
    )

#r2

def check_r2(holding, policy):
    venues = policy["approved_venues"]
    expected = "listed on one of: " + ", ".join(venues)

    asset_type = str(holding.get("asset_type", "")).strip().lower()
    listing_status = str(holding.get("listing_status", "")).strip().lower()
    exchange = str(holding.get("exchange", "")).strip().upper()

    if asset_type not in ("equity", "bond"):
        status = "NOT_APPLICABLE"
        observed_field = "asset_type"
        observed_value = asset_type
        expected = "—"
        reason = "Listing rule applies to equities and bonds only"

    elif listing_status == "":
        status = "REVIEW"
        observed_field = "listing_status"
        observed_value = listing_status
        reason = "Listing status is missing, so the rule cannot be evaluated"

    elif listing_status != "listed":
        status = "FAIL"
        observed_field = "listing_status"
        observed_value = listing_status
        reason = "Instrument is not listed on a public market"

    elif exchange == "":
        status = "REVIEW"
        observed_field = "exchange"
        observed_value = exchange
        reason = "Instrument is marked as listed but no trading venue is given"

    elif exchange in venues:
        status = "PASS"
        observed_field = "exchange"
        observed_value = exchange
        reason = "Instrument is listed on an approved trading venue"

    else:
        status = "FAIL"
        observed_field = "exchange"
        observed_value = exchange
        reason = "Trading venue is not on the approved venue list"

    return RuleResult(
        rule_id="R2",
        rule_name="Listing requirement",
        status=status,
        observed_field=observed_field,
        observed_value=observed_value,
        expected=expected,
        reason=reason,
    )


#r3

def check_r3(holding, policy):
    """R3 - funds must be on the approved fund list."""
    approved_isins = {
        str(f["isin"]).strip().upper() for f in policy["approved_funds"]
    }
    expected = "ISIN must be on the approved fund list"

    asset_type = str(holding.get("asset_type", "")).strip().lower()
    isin = str(holding.get("isin", "")).strip().upper()

    if asset_type != "fund":
        status = "NOT_APPLICABLE"
        observed_field = "asset_type"
        observed_value = asset_type
        expected = "—"
        reason = "Approved fund rule applies to funds only"

    elif isin == "":
        status = "REVIEW"
        observed_field = "isin"
        observed_value = isin
        reason = "Fund has no ISIN, so it cannot be checked against the approved list"

    elif isin in approved_isins:
        status = "PASS"
        observed_field = "isin"
        observed_value = isin
        reason = "Fund is on the approved fund list"

    else:
        status = "FAIL"
        observed_field = "isin"
        observed_value = isin
        reason = "Fund is not on the approved fund list"

    return RuleResult(
        rule_id="R3",
        rule_name="Approved fund universe",
        status=status,
        observed_field=observed_field,
        observed_value=observed_value,
        expected=expected,
        reason=reason,
    )


def check_r4(holding, policy):
    """R4 - bonds must have a credit rating at or above the policy minimum."""
    scale = policy["rating_scale"]
    minimum = str(policy["minimum_rating"]).strip().upper()
    unrated = {str(v).strip().upper() for v in policy["unrated_values"]}
    expected = f"{minimum} or better"

    asset_type = str(holding.get("asset_type", "")).strip().lower()
    rating = str(holding.get("rating", "")).strip().upper()

    if asset_type != "bond":
        status = "NOT_APPLICABLE"
        observed_field = "asset_type"
        observed_value = asset_type
        expected = "—"
        reason = "Credit rating rule applies to bonds only"

    elif rating in unrated:
        status = "REVIEW"
        observed_field = "rating"
        observed_value = rating
        reason = "Bond has no usable credit rating, so the rule cannot be evaluated"

    elif rating not in scale:
        status = "REVIEW"
        observed_field = "rating"
        observed_value = rating
        reason = "Bond rating is not recognised in the policy rating scale"

    elif scale.index(rating) <= scale.index(minimum):
        status = "PASS"
        observed_field = "rating"
        observed_value = rating
        reason = "Bond rating meets the minimum permitted rating"

    else:
        status = "FAIL"
        observed_field = "rating"
        observed_value = rating
        reason = "Bond rating is below the minimum permitted rating"

    return RuleResult(
        rule_id="R4",
        rule_name="Minimum credit rating",
        status=status,
        observed_field=observed_field,
        observed_value=observed_value,
        expected=expected,
        reason=reason,
    )


def check_r5(holding, policy):
    """R5 - securities issued by the insurer's own group are not permitted."""
    insurer_group = str(policy["insurer_group"]).strip().upper()
    expected = f"issuer group must not be {insurer_group}"

    issuer_group = str(holding.get("issuer_group", "")).strip().upper()

    if issuer_group == "":
        status = "REVIEW"
        reason = "Issuer group is missing, so the rule cannot be evaluated"

    elif issuer_group == insurer_group:
        status = "FAIL"
        reason = "Security is issued by the insurer's own group"

    else:
        status = "PASS"
        reason = "Security is not issued by the insurer's own group"

    return RuleResult(
        rule_id="R5",
        rule_name="Own-group restriction",
        status=status,
        observed_field="issuer_group",
        observed_value=issuer_group,
        expected=expected,
        reason=reason,
    )

def evaluate_holding(holding, policy):
    """Run all five rules against one holding and derive its overall status."""
    results = [
        check_r1(holding, policy),
        check_r2(holding, policy),
        check_r3(holding, policy),
        check_r4(holding, policy),
        check_r5(holding, policy),
    ]

    statuses = [r.status for r in results]

    if "FAIL" in statuses:
        overall = "REJECTED"
    elif "REVIEW" in statuses:
        overall = "REVIEW"
    else:
        overall = "APPROVED"

    return {
        "account_id": holding.get("account_id", ""),
        "isin": holding.get("isin", ""),
        "name": holding.get("name", ""),
        "asset_type": holding.get("asset_type", ""),
        "market_value": holding.get("market_value", ""),
        "status": overall,
        "rule_results": results,
    }