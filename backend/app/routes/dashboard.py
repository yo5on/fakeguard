from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Analysis
from ..queries import RISK_CATEGORIES, latest_analysis_ids
from ..schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def _latest_category_stats(db: Session):
    """Count and score-sum of latest analyses per category, computed in SQL."""
    latest = latest_analysis_ids(db)
    rows = (
        db.query(Analysis.category, func.count(Analysis.id), func.sum(Analysis.risk_score))
        .join(latest, Analysis.id == latest.c.analysis_id)
        .group_by(Analysis.category)
        .all()
    )
    return {category: (count, total or 0.0) for category, count, total in rows}

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary statistics.
    """
    total_accounts = db.query(func.count(Account.id)).scalar() or 0
    stats = _latest_category_stats(db)

    analyzed = sum(count for count, _ in stats.values())
    score_sum = sum(total for _, total in stats.values())
    avg_risk_score = score_sum / analyzed if analyzed else 0.0

    def count_of(category: str) -> int:
        return stats.get(category, (0, 0.0))[0]

    return {
        "total_accounts": total_accounts,
        "low_risk": count_of("LOW"),
        "medium_risk": count_of("MEDIUM"),
        "high_risk": count_of("HIGH"),
        "critical_risk": count_of("CRITICAL"),
        "average_risk_score": round(avg_risk_score, 2)
    }

@router.get("/distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Get risk distribution data for charts.
    """
    stats = _latest_category_stats(db)
    return {
        "distribution": [
            {"category": category, "count": stats.get(category, (0, 0.0))[0]}
            for category in RISK_CATEGORIES
        ]
    }

@router.get("/top-risk")
def get_top_risk_accounts(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top high-risk accounts for priority review.
    """
    latest = latest_analysis_ids(db)
    top_accounts = (
        db.query(Account, Analysis)
        .join(latest, Account.id == latest.c.account_id)
        .join(Analysis, Analysis.id == latest.c.analysis_id)
        .order_by(Analysis.risk_score.desc(), Account.id.asc())
        .limit(limit)
        .all()
    )

    return {
        "accounts": [
            {
                "id": account.id,
                "username": account.username,
                "risk_score": analysis.risk_score,
                "category": analysis.category,
                "last_analyzed": analysis.created_at
            }
            for account, analysis in top_accounts
        ]
    }
