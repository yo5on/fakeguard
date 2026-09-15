from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    age_days = Column(Integer, nullable=False)
    followers = Column(Integer, nullable=False)
    following = Column(Integer, nullable=False)
    posts_per_day = Column(Float, nullable=False)
    profile_completeness = Column(Float, nullable=False)
    avg_likes = Column(Float, nullable=False)
    avg_comments = Column(Float, nullable=False)
    archetype = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="account", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    recommended_action = Column(String(255), nullable=False)
    analysis_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="analyses")