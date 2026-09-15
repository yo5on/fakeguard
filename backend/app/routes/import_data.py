from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import io
from typing import List

from ..database import get_db
from ..models import Account
from ..schemas import ImportResult, AccountCreate

router = APIRouter(prefix="/api/import", tags=["import"])

@router.post("/csv", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import accounts from CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
    
    required_columns = [
        'username', 'age_days', 'followers', 'following',
        'posts_per_day', 'profile_completeness', 'avg_likes', 'avg_comments'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Validate data
            account_data = {
                'username': str(row['username']),
                'age_days': int(row['age_days']),
                'followers': int(row['followers']),
                'following': int(row['following']),
                'posts_per_day': float(row['posts_per_day']),
                'profile_completeness': float(row['profile_completeness']),
                'avg_likes': float(row['avg_likes']),
                'avg_comments': float(row['avg_comments']),
                'archetype': str(row['archetype']) if 'archetype' in row and pd.notna(row['archetype']) else None
            }
            
            # Validate using Pydantic
            validated = AccountCreate(**account_data)
            
            # Check if username already exists
            existing = db.query(Account).filter(
                Account.username == validated.username
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Create account
            db_account = Account(**validated.model_dump())
            db.add(db_account)
            imported += 1
            
        except ValueError as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
            skipped += 1
        except Exception as e:
            errors.append(f"Row {idx + 2}: Validation error - {str(e)}")
            skipped += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:50]  # Limit error messages
    }