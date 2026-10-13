import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Analysis, utcnow
from ..queries import analysis_details
from ..schemas import AccountCreate, AnalysisResponse
from ..scoring.risk_engine import analyze_account

router = APIRouter(prefix="/api", tags=["analysis"])

def _run_analysis(account) -> dict:
    return analyze_account(
        username=account.username,
        age_days=account.age_days,
        followers=account.followers,
        following=account.following,
        posts_per_day=account.posts_per_day,
        profile_completeness=account.profile_completeness,
        avg_likes=account.avg_likes,
        avg_comments=account.avg_comments
    )

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_new_account(account_data: AccountCreate):
    """
    Analyze a new account without saving it to the database.
    """
    analysis_result = _run_analysis(account_data)
    now = utcnow()

    # Temporary account object for the response (id 0 = not persisted)
    temp_account = {
        "id": 0,
        **account_data.model_dump(),
        "created_at": now,
        "updated_at": now
    }

    return {
        "account": temp_account,
        "analysis": analysis_result,
        "timestamp": now
    }

@router.post("/accounts/{account_id}/analyze", response_model=AnalysisResponse)
def analyze_existing_account(account_id: int, db: Session = Depends(get_db)):
    """
    Analyze an existing account and store the analysis result.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    analysis_result = _run_analysis(account)

    new_analysis = Analysis(
        account_id=account.id,
        risk_score=analysis_result["risk_score"],
        category=analysis_result["category"],
        recommended_action=analysis_result["recommended_action"],
        analysis_json=json.dumps(analysis_result)
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return {
        "account": account,
        "analysis": analysis_result,
        "timestamp": new_analysis.created_at
    }

@router.get("/accounts/{account_id}/analysis")
def get_account_analyses(account_id: int, db: Session = Depends(get_db)):
    """
    Get all analyses for a specific account, newest first.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    analyses = db.query(Analysis).filter(
        Analysis.account_id == account_id
    ).order_by(Analysis.id.desc()).all()

    result = [
        {
            "id": analysis.id,
            "risk_score": analysis.risk_score,
            "category": analysis.category,
            "recommended_action": analysis.recommended_action,
            "details": analysis_details(analysis),
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]

    return {
        "account_id": account_id,
        "username": account.username,
        "analyses": result
    }
