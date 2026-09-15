from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Account, Analysis
from ..schemas import DashboardSummary, RiskDistribution, TopRiskAccount

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary statistics.
    """
    total_accounts = db.query(Account).count()
    
    # Get latest analysis for each account
    latest_analyses_subquery = db.query(
        Analysis.account_id,
        func.max(Analysis.created_at).label('max_created_at')
    ).group_by(Analysis.account_id).subquery()
    
    latest_analyses = db.query(Analysis).join(
        latest_analyses_subquery,
        (Analysis.account_id == latest_analyses_subquery.c.account_id) &
        (Analysis.created_at == latest_analyses_subquery.c.max_created_at)
    ).all()
    
    # Count by category
    low_risk = sum(1 for a in latest_analyses if a.category == "LOW")
    medium_risk = sum(1 for a in latest_analyses if a.category == "MEDIUM")
    high_risk = sum(1 for a in latest_analyses if a.category == "HIGH")
    critical_risk = sum(1 for a in latest_analyses if a.category == "CRITICAL")
    
    # Calculate average risk score
    if latest_analyses:
        avg_risk_score = sum(a.risk_score for a in latest_analyses) / len(latest_analyses)
    else:
        avg_risk_score = 0.0
    
    return {
        "total_accounts": total_accounts,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk,
        "critical_risk": critical_risk,
        "average_risk_score": round(avg_risk_score, 2)
    }

@router.get("/distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Get risk distribution data for charts.
    """
    # Get latest analysis for each account
    latest_analyses_subquery = db.query(
        Analysis.account_id,
        func.max(Analysis.created_at).label('max_created_at')
    ).group_by(Analysis.account_id).subquery()
    
    latest_analyses = db.query(Analysis).join(
        latest_analyses_subquery,
        (Analysis.account_id == latest_analyses_subquery.c.account_id) &
        (Analysis.created_at == latest_analyses_subquery.c.max_created_at)
    ).all()
    
    # Count by category
    distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }
    
    for analysis in latest_analyses:
        distribution[analysis.category] = distribution.get(analysis.category, 0) + 1
    
    return {
        "distribution": [
            {"category": cat, "count": count}
            for cat, count in distribution.items()
        ]
    }

@router.get("/top-risk")
def get_top_risk_accounts(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get top high-risk accounts for priority review.
    """
    # Get latest analysis for each account
    latest_analyses_subquery = db.query(
        Analysis.account_id,
        func.max(Analysis.created_at).label('max_created_at')
    ).group_by(Analysis.account_id).subquery()
    
    top_accounts = db.query(
        Account, Analysis
    ).join(
        Analysis,
        Account.id == Analysis.account_id
    ).join(
        latest_analyses_subquery,
        (Analysis.account_id == latest_analyses_subquery.c.account_id) &
        (Analysis.created_at == latest_analyses_subquery.c.max_created_at)
    ).order_by(
        Analysis.risk_score.desc()
    ).limit(limit).all()
    
    result = []
    for account, analysis in top_accounts:
        result.append({
            "id": account.id,
            "username": account.username,
            "risk_score": analysis.risk_score,
            "category": analysis.category,
            "last_analyzed": analysis.created_at
        })
    
    return {"accounts": result}