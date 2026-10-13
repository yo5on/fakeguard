from typing import Optional, Tuple

from .thresholds import ACCOUNT_AGE, ENGAGEMENT, FOLLOWER_RATIO, POSTING_FREQUENCY

def calculate_account_age_risk(age_days: int) -> float:
    """
    Calculate risk score for account age.
    
    Args:
        age_days: Account age in days
        
    Returns:
        Risk score between 0-100
    """
    return ACCOUNT_AGE.risk_for(age_days)


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
    return FOLLOWER_RATIO.risk_for(followers / following), True


def calculate_posting_frequency_risk(posts_per_day: float) -> float:
    """
    Calculate risk score for posting frequency.
    
    Args:
        posts_per_day: Average posts per day
        
    Returns:
        Risk score between 0-100
    """
    return POSTING_FREQUENCY.risk_for(posts_per_day)


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
    return ENGAGEMENT.risk_for(engagement_rate), True

