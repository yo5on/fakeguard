from .thresholds import REASON_CODE_RULES, REASON_CODES

__all__ = ["REASON_CODES", "get_reason_codes"]


def get_reason_codes(features: dict) -> list:
    """
    Generate reason codes based on feature analysis.

    A code fires when its feature is available and the feature risk reaches
    the rule's ``min_feature_risk`` (see thresholds.REASON_CODE_RULES).

    Args:
        features: Dictionary of feature analyses keyed by feature name
            (account_age, follower_ratio, posting_frequency,
            profile_completeness, engagement)

    Returns:
        List of reason code dictionaries sorted by weighted contribution
    """
    reasons = []
    for rule in REASON_CODE_RULES:
        feature = features.get(rule.feature)
        if feature and feature["available"] and feature["risk_score"] >= rule.min_feature_risk:
            reasons.append({
                "code": rule.code,
                "description": rule.description,
                "feature": rule.feature,
                "feature_score": feature["risk_score"],
                "weighted_contribution": feature["weighted_contribution"]
            })

    # Sort by weighted contribution descending (stable, so ties keep code order)
    reasons.sort(key=lambda x: x["weighted_contribution"], reverse=True)

    return reasons
