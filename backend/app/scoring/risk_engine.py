from typing import Dict, List, Any
from .feature_rules import (
    calculate_account_age_risk,
    calculate_follower_ratio_risk,
    calculate_posting_frequency_risk,
    calculate_profile_completeness_risk,
    calculate_engagement_risk
)
from .reason_codes import get_reason_codes

# Feature weights (must sum to 100%)
FEATURE_WEIGHTS = {
    "account_age": 0.20,
    "follower_ratio": 0.25,
    "posting_frequency": 0.20,
    "profile_completeness": 0.15,
    "engagement": 0.20
}

def get_risk_category(score: float) -> str:
    """
    Determine risk category based on precise score.
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Risk category string
    """
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MEDIUM"
    elif score < 80:
        return "HIGH"
    else:
        return "CRITICAL"

def get_recommended_action(category: str) -> str:
    """
    Get recommended action based on risk category.
    
    Args:
        category: Risk category
        
    Returns:
        Recommended action string
    """
    actions = {
        "LOW": "No immediate action",
        "MEDIUM": "Monitor account",
        "HIGH": "Manual review recommended",
        "CRITICAL": "Priority investigation"
    }
    return actions.get(category, "Unknown")

def analyze_account(
    username: str,
    age_days: int,
    followers: int,
    following: int,
    posts_per_day: float,
    profile_completeness: float,
    avg_likes: float,
    avg_comments: float
) -> Dict[str, Any]:
    """
    Analyze an account and calculate risk score.
    
    Args:
        username: Account username
        age_days: Account age in days
        followers: Number of followers
        following: Number of following
        posts_per_day: Average posts per day
        profile_completeness: Profile completion percentage (0-100)
        avg_likes: Average likes per post
        avg_comments: Average comments per post
        
    Returns:
        Dictionary containing analysis results
    """
    features = {}
    total_weighted_score = 0.0
    total_weight_used = 0.0
    
    # Account Age
    age_risk = calculate_account_age_risk(age_days)
    age_weight = FEATURE_WEIGHTS["account_age"]
    age_contribution = age_risk * age_weight
    features["account_age"] = {
        "feature": "Account Age",
        "risk_score": age_risk,
        "weighted_contribution": age_contribution,
        "available": True,
        "details": f"{age_days} days old"
    }
    total_weighted_score += age_contribution
    total_weight_used += age_weight
    
    # Follower/Following Ratio
    ratio_risk, ratio_available = calculate_follower_ratio_risk(followers, following)
    ratio_weight = FEATURE_WEIGHTS["follower_ratio"]
    if ratio_available:
        ratio_contribution = ratio_risk * ratio_weight
        ratio_value = followers / following if following > 0 else 0
        features["follower_ratio"] = {
            "feature": "Follower/Following Ratio",
            "risk_score": ratio_risk,
            "weighted_contribution": ratio_contribution,
            "available": True,
            "details": f"Ratio: {ratio_value:.2f} ({followers}/{following})"
        }
        total_weighted_score += ratio_contribution
        total_weight_used += ratio_weight
    else:
        features["follower_ratio"] = {
            "feature": "Follower/Following Ratio",
            "risk_score": 0.0,
            "weighted_contribution": 0.0,
            "available": False,
            "details": "Cannot calculate (following = 0)"
        }
    
    # Posting Frequency
    posting_risk = calculate_posting_frequency_risk(posts_per_day)
    posting_weight = FEATURE_WEIGHTS["posting_frequency"]
    posting_contribution = posting_risk * posting_weight
    features["posting_frequency"] = {
        "feature": "Posting Frequency",
        "risk_score": posting_risk,
        "weighted_contribution": posting_contribution,
        "available": True,
        "details": f"{posts_per_day:.1f} posts/day"
    }
    total_weighted_score += posting_contribution
    total_weight_used += posting_weight
    
    # Profile Completeness
    profile_risk = calculate_profile_completeness_risk(profile_completeness)
    profile_weight = FEATURE_WEIGHTS["profile_completeness"]
    profile_contribution = profile_risk * profile_weight
    features["profile_completeness"] = {
        "feature": "Profile Completeness",
        "risk_score": profile_risk,
        "weighted_contribution": profile_contribution,
        "available": True,
        "details": f"{profile_completeness:.0f}% complete"
    }
    total_weighted_score += profile_contribution
    total_weight_used += profile_weight
    
    # Engagement
    engagement_risk, engagement_available = calculate_engagement_risk(avg_likes, avg_comments, followers)
    engagement_weight = FEATURE_WEIGHTS["engagement"]
    if engagement_available:
        engagement_contribution = engagement_risk * engagement_weight
        engagement_rate = ((avg_likes + avg_comments) / followers) * 100 if followers > 0 else 0
        features["engagement"] = {
            "feature": "Engagement",
            "risk_score": engagement_risk,
            "weighted_contribution": engagement_contribution,
            "available": True,
            "details": f"{engagement_rate:.2f}% engagement rate"
        }
        total_weighted_score += engagement_contribution
        total_weight_used += engagement_weight
    else:
        features["engagement"] = {
            "feature": "Engagement",
            "risk_score": 0.0,
            "weighted_contribution": 0.0,
            "available": False,
            "details": "Cannot calculate (followers = 0)"
        }
    
    # Calculate final score with renormalization
    if total_weight_used > 0:
        final_score = total_weighted_score / total_weight_used
    else:
        final_score = 0.0
    
    # Clamp score
    final_score = max(0.0, min(100.0, final_score))
    
    # Determine category and action
    category = get_risk_category(final_score)
    recommended_action = get_recommended_action(category)
    
    # Generate reason codes
    reason_codes = get_reason_codes(features)
    
    # Format feature list for response
    feature_list = [
        {
            "feature": details["feature"],
            "risk_score": details["risk_score"],
            "weighted_contribution": details["weighted_contribution"],
            "available": details["available"],
            "details": details.get("details")
        }
        for details in features.values()
    ]
    
    return {
        "risk_score": final_score,
        "category": category,
        "recommended_action": recommended_action,
        "features": feature_list,
        "reason_codes": reason_codes,
        "total_weight_used": total_weight_used
    }