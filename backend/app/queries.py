import json
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Account, Analysis

RISK_CATEGORIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def latest_analysis_ids(db: Session):
    """
    Subquery of the most recent analysis id per account.

    Uses max(id) rather than max(created_at): ids are monotonically increasing,
    and two analyses stored within the same timestamp would otherwise both
    match and duplicate the account row.
    """
    return (
        db.query(Analysis.account_id, func.max(Analysis.id).label("analysis_id"))
        .group_by(Analysis.account_id)
        .subquery()
    )


def account_to_dict(account: Account) -> Dict[str, Any]:
    return {
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
    }


def analysis_details(analysis: Analysis) -> Optional[Dict[str, Any]]:
    """Decode the stored analysis JSON, tolerating corrupt rows."""
    try:
        return json.loads(analysis.analysis_json)
    except (TypeError, ValueError):
        return None
