from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from ..database import get_db
from ..models import Account, Analysis
from ..schemas import AccountCreate, AnalysisResponse, AnalysisResult
from ..scoring.risk_engine import analyze_account

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_new_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    """
    Analyze a new account without saving it to the database.
    """
    # Perform analysis
    analysis_result = analyze_account(
        username=account_data.username,
        age_days=account_data.age_days,
        followers=account_data.followers,
        following=account_data.following,
        posts_per_day=account_data.posts_per_day,
        profile_completeness=account_data.profile_completeness,
        avg_likes=account_data.avg_likes,
        avg_comments=account_data.avg_comments
    )
    
    # Create temporary account object for response
    temp_account = {
        "id": 0,
        "username": account_data.username,
        "age_days": account_data.age_days,
        "followers": account_data.followers,
        "following": account_data.following,
        "posts_per_day": account_data.posts_per_day,
        "profile_completeness": account_data.profile_completeness,
        "avg_likes": account_data.avg_likes,
        "avg_comments": account_data.avg_comments,
        "archetype": account_data.archetype,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return {
        "account": temp_account,
        "analysis": analysis_result,
        "timestamp": datetime.utcnow()
    }

@router.post("/accounts/{account_id}/analyze", response_model=AnalysisResponse)
def analyze_existing_account(account_id: int, db: Session = Depends(get_db)):
    """
    Analyze an existing account and store the analysis result.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Perform analysis
    analysis_result = analyze_account(
        username=account.username,
        age_days=account.age_days,
        followers=account.followers,
        following=account.following,
        posts_per_day=account.posts_per_day,
        profile_completeness=account.profile_completeness,
        avg_likes=account.avg_likes,
        avg_comments=account.avg_comments
    )
    
    # Store analysis
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
    Get all analyses for a specific account.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    analyses = db.query(Analysis).filter(
        Analysis.account_id == account_id
    ).order_by(Analysis.created_at.desc()).all()
    
    result = []
    for analysis in analyses:
        result.append({
            "id": analysis.id,
            "risk_score": analysis.risk_score,
            "category": analysis.category,
            "recommended_action": analysis.recommended_action,
            "details": json.loads(analysis.analysis_json),
            "created_at": analysis.created_at
        })
    
    return {
        "account_id": account_id,
        "username": account.username,
        "analyses": result
    }