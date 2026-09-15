import pytest
from app.scoring.risk_engine import analyze_account, get_risk_category, get_recommended_action

def test_get_risk_category():
    """Test risk category determination."""
    assert get_risk_category(0) == "LOW"
    assert get_risk_category(29.9) == "LOW"
    assert get_risk_category(30.0) == "MEDIUM"
    assert get_risk_category(59.9) == "MEDIUM"
    assert get_risk_category(60.0) == "HIGH"
    assert get_risk_category(79.9) == "HIGH"
    assert get_risk_category(80.0) == "CRITICAL"
    assert get_risk_category(100.0) == "CRITICAL"

def test_get_recommended_action():
    """Test recommended action determination."""
    assert get_recommended_action("LOW") == "No immediate action"
    assert get_recommended_action("MEDIUM") == "Monitor account"
    assert get_recommended_action("HIGH") == "Manual review recommended"
    assert get_recommended_action("CRITICAL") == "Priority investigation"

def test_analyze_normal_account():
    """Test analysis of a normal account."""
    result = analyze_account(
        username="normal_user",
        age_days=500,
        followers=1000,
        following=800,
        posts_per_day=3.0,
        profile_completeness=90.0,
        avg_likes=50.0,
        avg_comments=5.0
    )
    
    assert result["category"] == "LOW"
    assert result["risk_score"] < 30
    assert len(result["features"]) == 5
    assert all(f["available"] for f in result["features"])

def test_analyze_suspicious_account():
    """Test analysis of a suspicious account."""
    result = analyze_account(
        username="suspicious_user",
        age_days=5,
        followers=10,
        following=5000,
        posts_per_day=50.0,
        profile_completeness=20.0,
        avg_likes=0.1,
        avg_comments=0.01
    )
    
    assert result["category"] == "CRITICAL"
    assert result["risk_score"] >= 80
    assert len(result["reason_codes"]) > 0

def test_analyze_zero_followers():
    """Test analysis with zero followers."""
    result = analyze_account(
        username="zero_followers",
        age_days=100,
        followers=0,
        following=500,
        posts_per_day=5.0,
        profile_completeness=80.0,
        avg_likes=0.0,
        avg_comments=0.0
    )
    
    # Should not crash
    assert "risk_score" in result
    assert "category" in result
    
    # Engagement should be unavailable
    engagement_feature = next(f for f in result["features"] if f["feature"] == "Engagement")
    assert engagement_feature["available"] is False
    
    # Should still calculate score from available features
    assert 0 <= result["risk_score"] <= 100

def test_analyze_zero_following():
    """Test analysis with zero following."""
    result = analyze_account(
        username="zero_following",
        age_days=200,
        followers=1000,
        following=0,
        posts_per_day=3.0,
        profile_completeness=90.0,
        avg_likes=50.0,
        avg_comments=5.0
    )
    
    # Should not crash
    assert "risk_score" in result
    assert "category" in result
    
    # Follower ratio should be unavailable
    ratio_feature = next(f for f in result["features"] if f["feature"] == "Follower/Following Ratio")
    assert ratio_feature["available"] is False
    
    # Should still calculate score from available features
    assert 0 <= result["risk_score"] <= 100

def test_analyze_both_zero():
    """Test analysis with both followers and following zero."""
    result = analyze_account(
        username="both_zero",
        age_days=50,
        followers=0,
        following=0,
        posts_per_day=2.0,
        profile_completeness=50.0,
        avg_likes=0.0,
        avg_comments=0.0
    )
    
    # Should not crash
    assert "risk_score" in result
    assert "category" in result
    
    # Both engagement and ratio should be unavailable
    engagement_feature = next(f for f in result["features"] if f["feature"] == "Engagement")
    ratio_feature = next(f for f in result["features"] if f["feature"] == "Follower/Following Ratio")
    
    assert engagement_feature["available"] is False
    assert ratio_feature["available"] is False
    
    # Should calculate from remaining 3 features
    assert result["total_weight_used"] < 1.0
    assert 0 <= result["risk_score"] <= 100

def test_score_boundaries():
    """Test that scores are clamped within 0-100."""
    # Very safe account
    result = analyze_account(
        username="very_safe",
        age_days=2000,
        followers=10000,
        following=500,
        posts_per_day=1.0,
        profile_completeness=100.0,
        avg_likes=1000.0,
        avg_comments=100.0
    )
    assert 0 <= result["risk_score"] <= 100
    
    # Very risky account
    result = analyze_account(
        username="very_risky",
        age_days=1,
        followers=5,
        following=10000,
        posts_per_day=200.0,
        profile_completeness=0.0,
        avg_likes=0.0,
        avg_comments=0.0
    )
    assert 0 <= result["risk_score"] <= 100

def test_weighted_contributions_sum():
    """Test that weighted contributions are calculated correctly."""
    result = analyze_account(
        username="test_user",
        age_days=100,
        followers=1000,
        following=800,
        posts_per_day=5.0,
        profile_completeness=75.0,
        avg_likes=50.0,
        avg_comments=5.0
    )
    
    # Sum of weighted contributions should equal risk score * total_weight_used
    total_contribution = sum(f["weighted_contribution"] for f in result["features"] if f["available"])
    expected_total = result["risk_score"] * result["total_weight_used"]
    
    # Allow small floating point difference
    assert abs(total_contribution - expected_total) < 0.01