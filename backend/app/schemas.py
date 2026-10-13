from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Upper bounds keep values inside SQLite's 64-bit integer range and reject
# obviously malformed input; they are far above any real-world account.
MAX_COUNT = 10_000_000_000
MAX_RATE = 1_000_000_000.0

class AccountBase(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    username: str = Field(..., min_length=1, max_length=255)
    age_days: int = Field(..., ge=0, le=MAX_COUNT)
    followers: int = Field(..., ge=0, le=MAX_COUNT)
    following: int = Field(..., ge=0, le=MAX_COUNT)
    posts_per_day: float = Field(..., ge=0, le=MAX_RATE)
    profile_completeness: float = Field(..., ge=0, le=100)
    avg_likes: float = Field(..., ge=0, le=MAX_RATE)
    avg_comments: float = Field(..., ge=0, le=MAX_RATE)
    archetype: Optional[str] = Field(None, max_length=100)

    @field_validator('username', mode='before')
    @classmethod
    def strip_username(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError('username cannot be blank')
        return v

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class FeatureAnalysis(BaseModel):
    feature: str
    risk_score: float
    weighted_contribution: float
    available: bool
    details: Optional[str] = None

class ReasonCode(BaseModel):
    code: str
    description: str
    feature: str
    feature_score: float
    weighted_contribution: float

class AnalysisResult(BaseModel):
    risk_score: float
    category: str
    recommended_action: str
    features: List[FeatureAnalysis]
    reason_codes: List[ReasonCode]
    total_weight_used: float

class AnalysisResponse(BaseModel):
    account: Account
    analysis: AnalysisResult
    timestamp: datetime

class AnalysisRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    risk_score: float
    category: str
    recommended_action: str
    created_at: datetime

class DashboardSummary(BaseModel):
    total_accounts: int
    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int
    average_risk_score: float

class RiskDistribution(BaseModel):
    category: str
    count: int

class TopRiskAccount(BaseModel):
    id: int
    username: str
    risk_score: float
    category: str
    last_analyzed: Optional[datetime]

class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: List[str]

class ScoringConfig(BaseModel):
    features: Dict[str, Any]
    categories: Dict[str, Any]
    reason_codes: Dict[str, str]
