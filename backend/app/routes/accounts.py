from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional

from ..database import get_db
from ..models import Account, Analysis
from ..schemas import Account as AccountSchema, AccountCreate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("")
def get_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = Query("id", regex="^(id|username|risk_score|age_days|followers|following)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Get accounts with pagination, search, filtering, and sorting.
    """
    query = db.query(Account)
    
    # Apply search filter
    if search:
        query = query.filter(Account.username.contains(search))
    
    # Get latest analysis for each account if category filter is applied
    if category:
        # Subquery to get latest analysis for each account
        latest_analyses = db.query(
            Analysis.account_id,
            func.max(Analysis.created_at).label('max_created_at')
        ).group_by(Analysis.account_id).subquery()
        
        # Join with analyses to filter by category
        query = query.join(
            Analysis,
            Account.id == Analysis.account_id
        ).join(
            latest_analyses,
            (Analysis.account_id == latest_analyses.c.account_id) &
            (Analysis.created_at == latest_analyses.c.max_created_at)
        ).filter(Analysis.category == category.upper())
    
    # Count total before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by == "risk_score":
        # Join with latest analysis for risk score sorting
        latest_analyses = db.query(
            Analysis.account_id,
            func.max(Analysis.created_at).label('max_created_at')
        ).group_by(Analysis.account_id).subquery()
        
        query = query.outerjoin(
            Analysis,
            Account.id == Analysis.account_id
        ).outerjoin(
            latest_analyses,
            (Analysis.account_id == latest_analyses.c.account_id) &
            (Analysis.created_at == latest_analyses.c.max_created_at)
        )
        
        if sort_order == "desc":
            query = query.order_by(Analysis.risk_score.desc().nullslast())
        else:
            query = query.order_by(Analysis.risk_score.asc().nullsfirst())
    else:
        # Sort by account fields
        order_column = getattr(Account, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Apply pagination
    accounts = query.offset(skip).limit(limit).all()
    
    # Get latest analysis for each account
    result = []
    for account in accounts:
        latest_analysis = db.query(Analysis).filter(
            Analysis.account_id == account.id
        ).order_by(Analysis.created_at.desc()).first()
        
        account_dict = {
            "id": account.id,
            "username": account.username,
            "age_days": account.age_days,
            "followers": account.followers,
            "following": account.following,
            "posts_per_day": account.posts_per_day,
            "profile_completeness": account.profile_completeness,
            "avg_likes": account.avg_likes,
            "avg_comments": account.avg_comments,
            "archetype": account.archetype,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
            "latest_analysis": None
        }
        
        if latest_analysis:
            account_dict["latest_analysis"] = {
                "risk_score": latest_analysis.risk_score,
                "category": latest_analysis.category,
                "created_at": latest_analysis.created_at
            }
        
        result.append(account_dict)
    
    return {
        "accounts": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    """
    Get a specific account with its latest analysis.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    latest_analysis = db.query(Analysis).filter(
        Analysis.account_id == account_id
    ).order_by(Analysis.created_at.desc()).first()
    
    result = {
        "id": account.id,
        "username": account.username,
        "age_days": account.age_days,
        "followers": account.followers,
        "following": account.following,
        "posts_per_day": account.posts_per_day,
        "profile_completeness": account.profile_completeness,
        "avg_likes": account.avg_likes,
        "avg_comments": account.avg_comments,
        "archetype": account.archetype,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
        "latest_analysis": None
    }
    
    if latest_analysis:
        import json
        result["latest_analysis"] = {
            "id": latest_analysis.id,
            "risk_score": latest_analysis.risk_score,
            "category": latest_analysis.category,
            "recommended_action": latest_analysis.recommended_action,
            "details": json.loads(latest_analysis.analysis_json),
            "created_at": latest_analysis.created_at
        }
    
    return result

@router.post("", response_model=AccountSchema, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new account.
    """
    # Check if username already exists
    existing = db.query(Account).filter(Account.username == account.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account