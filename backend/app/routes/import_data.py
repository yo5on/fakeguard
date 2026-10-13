import csv
import io
import json
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Analysis
from ..rate_limit import rate_limit
from ..schemas import AccountCreate, ImportResult
from ..scoring.risk_engine import analyze_account

router = APIRouter(prefix="/api/import", tags=["import"])

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
MAX_ERRORS_REPORTED = 50

REQUIRED_COLUMNS = [
    'username', 'age_days', 'followers', 'following',
    'posts_per_day', 'profile_completeness', 'avg_likes', 'avg_comments'
]

def _format_validation_error(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", ())) or "row"
        parts.append(f"{field}: {err.get('msg', 'invalid value')}")
    return "; ".join(parts)

@router.post(
    "/csv",
    response_model=ImportResult,
    dependencies=[Depends(rate_limit("import", "rate_limit_import_per_minute"))],
)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import accounts from a CSV file and store an initial risk analysis for each
    imported account, so the dashboard reflects the batch immediately.

    Rows whose username already exists (in the database or earlier in the same
    file) are skipped; invalid rows are reported.
    """
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)"
        )

    try:
        text = contents.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))
    columns = [c.strip() for c in (reader.fieldnames or [])]
    reader.fieldnames = columns

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )

    imported = 0
    skipped = 0
    errors = []
    seen_usernames = set()

    try:
        rows = list(reader)
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"Malformed CSV: {e}")

    # Line 1 is the header, so data rows start at line 2.
    for line_no, row in enumerate(rows, start=2):
        if not any((value or "").strip() for value in row.values() if isinstance(value, str)):
            continue  # ignore blank lines

        raw = {col: (row.get(col) or "").strip() for col in REQUIRED_COLUMNS}
        archetype = (row.get('archetype') or "").strip() or None

        try:
            # Pydantic does strict-enough coercion: "12.7" is rejected for int
            # fields instead of being silently truncated.
            validated = AccountCreate(**raw, archetype=archetype)
        except ValidationError as e:
            errors.append(f"Row {line_no}: {_format_validation_error(e)}")
            skipped += 1
            continue

        if validated.username in seen_usernames:
            skipped += 1
            continue

        existing = db.query(Account.id).filter(Account.username == validated.username).first()
        if existing:
            skipped += 1
            continue

        seen_usernames.add(validated.username)
        fields = validated.model_dump()
        result = analyze_account(**{k: v for k, v in fields.items() if k != "archetype"})
        account = Account(**fields)
        account.analyses.append(Analysis(
            risk_score=result["risk_score"],
            category=result["category"],
            recommended_action=result["recommended_action"],
            analysis_json=json.dumps(result),
        ))
        db.add(account)
        imported += 1

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while saving imported accounts")

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:MAX_ERRORS_REPORTED]
    }
