from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    """
    Stores timestamps as naive UTC (same on-disk format as before) and returns
    timezone-aware UTC datetimes, so API responses carry an explicit offset and
    browsers don't misinterpret them as local time.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


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
    created_at = Column(UTCDateTime, default=utcnow)
    updated_at = Column(UTCDateTime, default=utcnow, onupdate=utcnow)

    analyses = relationship("Analysis", back_populates="account", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    recommended_action = Column(String(255), nullable=False)
    analysis_json = Column(Text, nullable=False)
    created_at = Column(UTCDateTime, default=utcnow)

    account = relationship("Account", back_populates="analyses")
