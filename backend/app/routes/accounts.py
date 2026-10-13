from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Analysis
from ..queries import (
    RISK_CATEGORIES,
    account_to_dict,
    analysis_details,
    latest_analysis_ids,
)
from ..schemas import Account as AccountSchema, AccountCreate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

SortField = Literal["id", "username", "risk_score", "age_days", "followers", "following"]

@router.get("")
def get_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=255),
    category: Optional[str] = None,
    sort_by: SortField = "id",
    sort_order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db)
):
    """
    Get accounts with pagination, search, filtering, and sorting.
    """
    if category:
        category = category.strip().upper()
        if category not in RISK_CATEGORIES:
            raise HTTPException(
                status_code=422,
                detail=f"category must be one of: {', '.join(RISK_CATEGORIES)}"
            )

    # Every account is outer-joined to at most one row: its latest analysis.
    latest = latest_analysis_ids(db)
    query = (
        db.query(Account, Analysis)
        .outerjoin(latest, Account.id == latest.c.account_id)
        .outerjoin(Analysis, Analysis.id == latest.c.analysis_id)
    )

    if search and search.strip():
        # autoescape so '_' and '%' in usernames are matched literally
        query = query.filter(Account.username.contains(search.strip(), autoescape=True))

    if category:
        query = query.filter(Analysis.category == category)

    total = query.count()

    if sort_by == "risk_score":
        if sort_order == "desc":
            query = query.order_by(Analysis.risk_score.desc().nullslast(), Account.id.asc())
        else:
            query = query.order_by(Analysis.risk_score.asc().nullsfirst(), Account.id.asc())
    else:
        order_column = getattr(Account, sort_by)
        primary = order_column.desc() if sort_order == "desc" else order_column.asc()
        # Secondary key keeps pagination stable when values tie.
        query = query.order_by(primary, Account.id.asc())

    rows = query.offset(skip).limit(limit).all()

    result = []
    for account, latest_analysis in rows:
        account_dict = account_to_dict(account)
        account_dict["latest_analysis"] = None
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
    ).order_by(Analysis.id.desc()).first()

    result = account_to_dict(account)
    result["latest_analysis"] = None

    if latest_analysis:
        result["latest_analysis"] = {
            "id": latest_analysis.id,
            "risk_score": latest_analysis.risk_score,
            "category": latest_analysis.category,
            "recommended_action": latest_analysis.recommended_action,
            "details": analysis_details(latest_analysis),
            "created_at": latest_analysis.created_at
        }

    return result

@router.post("", response_model=AccountSchema, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new account.
    """
    existing = db.query(Account).filter(Account.username == account.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_account = Account(**account.model_dump())
    db.add(db_account)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request created the same username after our check.
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    db.refresh(db_account)
    return db_account
