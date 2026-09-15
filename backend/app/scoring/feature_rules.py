from typing import Tuple, Optional

def calculate_account_age_risk(age_days: int) -> float:
    """
    Calculate risk score for account age.
    
    Args:
        age_days: Account age in days
        
    Returns:
        Risk score between 0-100
    """
    if age_days > 365:
        return 0.0
    elif age_days >= 180:
        return 10.0
    elif age_days >= 90:
        return 25.0
    elif age_days >= 30:
        return 45.0
    elif age_days >= 7:
        return 70.0
    else:
        return 90.0

def calculate_follower_ratio_risk(followers: int, following: int) -> Tuple[Optional[float], bool]:
    """
    Calculate risk score for follower/following ratio.
    
    Args:
        followers: Number of followers
        following: Number of following
        
    Returns:
        Tuple of (risk_score, is_available)
        risk_score is None if ratio cannot be calculated
    """
    if following == 0:
        return None, False
    
    ratio = followers / following
    
    if ratio >= 1.0:
        return 0.0, True
    elif ratio >= 0.5:
        return 20.0, True
    elif ratio >= 0.2:
        return 40.0, True
    elif ratio >= 0.05:
        return 70.0, True
    else:
        return 90.0, True

def calculate_posting_frequency_risk(posts_per_day: float) -> float:
    """
    Calculate risk score for posting frequency.
    
    Args:
        posts_per_day: Average posts per day
        
    Returns:
        Risk score between 0-100
    """
    if posts_per_day <= 5:
        return 0.0
    elif posts_per_day <= 10:
        return 20.0
    elif posts_per_day <= 20:
        return 40.0
    elif posts_per_day <= 50:
        return 70.0
    else:
        return 90.0

def calculate_profile_completeness_risk(profile_completeness: float) -> float:
    """
    Calculate risk score for profile completeness.
    
    Args:
        profile_completeness: Profile completion percentage (0-100)
        
    Returns:
        Risk score between 0-100
    """
    return 100.0 - profile_completeness

def calculate_engagement_risk(avg_likes: float, avg_comments: float, followers: int) -> Tuple[Optional[float], bool]:
    """
    Calculate risk score for engagement rate.
    
    Args:
        avg_likes: Average likes per post
        avg_comments: Average comments per post
        followers: Number of followers
        
    Returns:
        Tuple of (risk_score, is_available)
        risk_score is None if engagement cannot be calculated
    """
    if followers == 0:
        return None, False
    
    engagement_rate = ((avg_likes + avg_comments) / followers) * 100
    
    if engagement_rate >= 10:
        return 0.0, True
    elif engagement_rate >= 5:
        return 20.0, True
    elif engagement_rate >= 2:
        return 40.0, True
    elif engagement_rate >= 0.5:
        return 70.0, True
    else:
        return 90.0, True