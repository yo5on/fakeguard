from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class AccountBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    age_days: int = Field(..., ge=0)
    followers: int = Field(..., ge=0)
    following: int = Field(..., ge=0)
    posts_per_day: float = Field(..., ge=0)
    profile_completeness: float = Field(..., ge=0, le=100)
    avg_likes: float = Field(..., ge=0)
    avg_comments: float = Field(..., ge=0)
    archetype: Optional[str] = None

    @field_validator('age_days', 'followers', 'following', 'posts_per_day', 
                     'avg_likes', 'avg_comments', 'profile_completeness')
    @classmethod
    def check_non_negative(cls, v, info):
        if v < 0:
            raise ValueError(f'{info.field_name} cannot be negative')
        return v

    @field_validator('profile_completeness')
    @classmethod
    def check_profile_completeness_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError('profile_completeness must be between 0 and 100')
        return v

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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
    id: int
    account_id: int
    risk_score: float
    category: str
    recommended_action: str
    created_at: datetime

    class Config:
        from_attributes = True

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