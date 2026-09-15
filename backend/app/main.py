from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .database import init_db
from .routes import analysis, accounts, dashboard, import_data

load_dotenv()

app = FastAPI(
    title="FakeGuard API",
    description="Social Media Account Risk Analyzer",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include routers
app.include_router(analysis.router)
app.include_router(accounts.router)
app.include_router(dashboard.router)
app.include_router(import_data.router)

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fakeguard-api"}

@app.get("/api/config/scoring")
def get_scoring_config():
    """Get scoring configuration and methodology."""
    from .scoring.risk_engine import FEATURE_WEIGHTS
    from .scoring.reason_codes import REASON_CODES
    
    return {
        "features": {
            "account_age": {
                "weight": FEATURE_WEIGHTS["account_age"],
                "thresholds": {
                    ">365 days": 0,
                    "180-365 days": 10,
                    "90-179 days": 25,
                    "30-89 days": 45,
                    "7-29 days": 70,
                    "0-6 days": 90
                }
            },
            "follower_ratio": {
                "weight": FEATURE_WEIGHTS["follower_ratio"],
                "thresholds": {
                    ">=1.0": 0,
                    "0.5-0.99": 20,
                    "0.2-0.49": 40,
                    "0.05-0.19": 70,
                    "<0.05": 90
                }
            },
            "posting_frequency": {
                "weight": FEATURE_WEIGHTS["posting_frequency"],
                "thresholds": {
                    "<=5 posts/day": 0,
                    "6-10 posts/day": 20,
                    "11-20 posts/day": 40,
                    "21-50 posts/day": 70,
                    ">50 posts/day": 90
                }
            },
            "profile_completeness": {
                "weight": FEATURE_WEIGHTS["profile_completeness"],
                "formula": "risk = 100 - completeness"
            },
            "engagement": {
                "weight": FEATURE_WEIGHTS["engagement"],
                "thresholds": {
                    ">=10%": 0,
                    "5-9.9%": 20,
                    "2-4.9%": 40,
                    "0.5-1.9%": 70,
                    "<0.5%": 90
                }
            }
        },
        "categories": {
            "LOW": {"range": "0-29.9", "action": "No immediate action"},
            "MEDIUM": {"range": "30-59.9", "action": "Monitor account"},
            "HIGH": {"range": "60-79.9", "action": "Manual review recommended"},
            "CRITICAL": {"range": "80-100", "action": "Priority investigation"}
        },
        "reason_codes": REASON_CODES,
        "disclaimer": "The scoring weights and thresholds are prototype heuristics intended for demonstration and evaluation. They are not official government, law-enforcement, or social-media-platform standards."
    }