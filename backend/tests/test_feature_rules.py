import pytest
from app.scoring.feature_rules import (
    calculate_account_age_risk,
    calculate_follower_ratio_risk,
    calculate_posting_frequency_risk,
    calculate_profile_completeness_risk,
    calculate_engagement_risk
)

def test_account_age_risk():
    """Test account age risk calculation."""
    assert calculate_account_age_risk(400) == 0.0
    assert calculate_account_age_risk(200) == 10.0
    assert calculate_account_age_risk(100) == 25.0
    assert calculate_account_age_risk(50) == 45.0
    assert calculate_account_age_risk(15) == 70.0
    assert calculate_account_age_risk(3) == 90.0
    assert calculate_account_age_risk(0) == 90.0

def test_follower_ratio_risk():
    """Test follower/following ratio risk calculation."""
    # Normal ratios
    risk, available = calculate_follower_ratio_risk(1000, 500)
    assert available is True
    assert risk == 0.0
    
    risk, available = calculate_follower_ratio_risk(500, 1000)
    assert available is True
    assert risk == 20.0
    
    risk, available = calculate_follower_ratio_risk(200, 1000)
    assert available is True
    assert risk == 40.0
    
    risk, available = calculate_follower_ratio_risk(50, 1000)
    assert available is True
    assert risk == 70.0
    
    risk, available = calculate_follower_ratio_risk(10, 1000)
    assert available is True
    assert risk == 90.0
    
    # Edge case: following = 0
    risk, available = calculate_follower_ratio_risk(1000, 0)
    assert available is False
    assert risk is None

def test_posting_frequency_risk():
    """Test posting frequency risk calculation."""
    assert calculate_posting_frequency_risk(3.0) == 0.0
    assert calculate_posting_frequency_risk(7.0) == 20.0
    assert calculate_posting_frequency_risk(15.0) == 40.0
    assert calculate_posting_frequency_risk(30.0) == 70.0
    assert calculate_posting_frequency_risk(100.0) == 90.0

def test_profile_completeness_risk():
    """Test profile completeness risk calculation."""
    assert calculate_profile_completeness_risk(100.0) == 0.0
    assert calculate_profile_completeness_risk(80.0) == 20.0
    assert calculate_profile_completeness_risk(60.0) == 40.0
    assert calculate_profile_completeness_risk(40.0) == 60.0
    assert calculate_profile_completeness_risk(20.0) == 80.0
    assert calculate_profile_completeness_risk(0.0) == 100.0

def test_engagement_risk():
    """Test engagement rate risk calculation."""
    # High engagement
    risk, available = calculate_engagement_risk(100, 10, 1000)
    assert available is True
    assert risk == 0.0
    
    # Medium engagement
    risk, available = calculate_engagement_risk(60, 10, 1000)
    assert available is True
    assert risk == 20.0
    
    # Low engagement
    risk, available = calculate_engagement_risk(25, 5, 1000)
    assert available is True
    assert risk == 40.0
    
    # Very low engagement
    risk, available = calculate_engagement_risk(8, 2, 1000)
    assert available is True
    assert risk == 70.0
    
    # Extremely low engagement
    risk, available = calculate_engagement_risk(2, 0, 1000)
    assert available is True
    assert risk == 90.0
    
    # Edge case: followers = 0
    risk, available = calculate_engagement_risk(10, 5, 0)
    assert available is False
    assert risk is None

def test_edge_cases():
    """Test edge cases for all features."""
    # Zero values
    assert calculate_account_age_risk(0) == 90.0
    
    ratio_risk, available = calculate_follower_ratio_risk(0, 0)
    assert available is False
    
    assert calculate_posting_frequency_risk(0) == 0.0
    
    assert calculate_profile_completeness_risk(0) == 100.0
    
    eng_risk, available = calculate_engagement_risk(0, 0, 0)
    assert available is False