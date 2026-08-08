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