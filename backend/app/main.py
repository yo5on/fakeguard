import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings, log_startup_warnings
from .database import init_db
from .rate_limit import rate_limit
from .routes import analysis, accounts, auth, dashboard, import_data
from .routes.auth import require_auth
from .scoring.thresholds import scoring_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_startup_warnings(get_settings())
    init_db()
    yield


app = FastAPI(
    title="FakeGuard API",
    description="Social Media Account Risk Analyzer",
    version="1.2.0",
    lifespan=lifespan,
)


def parse_cors_origins(value: str) -> list[str]:
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


# CORS configuration. Auth uses a bearer token in the Authorization header (no
# cookies), so credentials stay disabled and a wildcard origin can't be abused
# for cookie-authenticated requests.
cors_origins = parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:5173"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting runs before authentication so unauthenticated floods are
# throttled too. Health and the public scoring methodology stay open.
protected = [
    Depends(rate_limit("api", "rate_limit_api_per_minute")),
    Depends(require_auth),
]

app.include_router(auth.router)
app.include_router(analysis.router, dependencies=protected)
app.include_router(accounts.router, dependencies=protected)
app.include_router(dashboard.router, dependencies=protected)
app.include_router(import_data.router, dependencies=protected)

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fakeguard-api"}

@app.get("/api/config/scoring")
def get_scoring_config():
    """Scoring configuration and methodology, generated from the same tables the engine uses."""
    return scoring_config()
