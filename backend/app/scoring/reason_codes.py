REASON_CODES = {
    "R01": "Very new account",
    "R02": "Extremely low follower/following ratio",
    "R03": "High posting frequency",
    "R04": "Incomplete profile",
    "R05": "Very low engagement"
}

def get_reason_codes(features: dict) -> list:
    """
    Generate reason codes based on feature analysis.
    
    Args:
        features: Dictionary of feature analyses with keys:
            - account_age
            - follower_ratio
            - posting_frequency
            - profile_completeness
            - engagement
            
    Returns:
        List of reason code dictionaries sorted by weighted contribution
    """
    reasons = []
    
    # R01: Very new account (age_days < 30)
    age_feature = features.get("account_age")
    if age_feature and age_feature["available"] and age_feature["risk_score"] >= 45:
        reasons.append({
            "code": "R01",
            "description": REASON_CODES["R01"],
            "feature": "account_age",
            "feature_score": age_feature["risk_score"],
            "weighted_contribution": age_feature["weighted_contribution"]
        })
    
    # R02: Extremely low follower/following ratio (ratio < 0.2)
    ratio_feature = features.get("follower_ratio")
    if ratio_feature and ratio_feature["available"] and ratio_feature["risk_score"] >= 40:
        reasons.append({
            "code": "R02",
            "description": REASON_CODES["R02"],
            "feature": "follower_ratio",
            "feature_score": ratio_feature["risk_score"],
            "weighted_contribution": ratio_feature["weighted_contribution"]
        })
    
    # R03: High posting frequency (posts_per_day > 20)
    posting_feature = features.get("posting_frequency")
    if posting_feature and posting_feature["available"] and posting_feature["risk_score"] >= 40:
        reasons.append({
            "code": "R03",
            "description": REASON_CODES["R03"],
            "feature": "posting_frequency",
            "feature_score": posting_feature["risk_score"],
            "weighted_contribution": posting_feature["weighted_contribution"]
        })
    
    # R04: Incomplete profile (completeness < 60%)
    profile_feature = features.get("profile_completeness")
    if profile_feature and profile_feature["available"] and profile_feature["risk_score"] >= 40:
        reasons.append({
            "code": "R04",
            "description": REASON_CODES["R04"],
            "feature": "profile_completeness",
            "feature_score": profile_feature["risk_score"],
            "weighted_contribution": profile_feature["weighted_contribution"]
        })
    
    # R05: Very low engagement (engagement_rate < 2%)
    engagement_feature = features.get("engagement")
    if engagement_feature and engagement_feature["available"] and engagement_feature["risk_score"] >= 40:
        reasons.append({
            "code": "R05",
            "description": REASON_CODES["R05"],
            "feature": "engagement",
            "feature_score": engagement_feature["risk_score"],
            "weighted_contribution": engagement_feature["weighted_contribution"]
        })
    
    # Sort by weighted contribution descending
    reasons.sort(key=lambda x: x["weighted_contribution"], reverse=True)
    
    return reasons