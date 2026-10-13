from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..rate_limit import rate_limit
from ..security import check_credentials, create_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

ANONYMOUS_USER = "anonymous"


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=1024)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int
    username: str


class AuthStatus(BaseModel):
    auth_required: bool
    auth_configured: bool


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _not_configured() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail="Authentication is not configured on the server. Set AUTH_USERNAME, "
               "AUTH_PASSWORD_HASH and AUTH_SECRET_KEY (or AUTH_DISABLED=true for local development).",
    )


def require_auth(request: Request, settings: Settings = Depends(get_settings)) -> str:
    """
    Dependency for protected routes. Returns the authenticated username.

    Fails closed: when authentication is neither configured nor explicitly
    disabled, protected routes answer 503 instead of serving data.
    """
    if settings.auth_disabled:
        return ANONYMOUS_USER
    if not settings.auth_configured:
        raise _not_configured()

    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise _unauthorized("Not authenticated")

    payload = decode_token(token.strip(), settings.auth_secret_key)
    if payload is None or payload["sub"] != settings.auth_username:
        raise _unauthorized("Invalid or expired token")
    return payload["sub"]


@router.get("/status", response_model=AuthStatus)
def auth_status(settings: Settings = Depends(get_settings)):
    """Public: tells the frontend whether it must show the login screen."""
    return {"auth_required": not settings.auth_disabled, "auth_configured": settings.auth_configured}


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit("login", "rate_limit_login_per_minute"))],
)
def login(credentials: LoginRequest, settings: Settings = Depends(get_settings)):
    if settings.auth_disabled:
        raise HTTPException(status_code=400, detail="Authentication is disabled on this server")
    if not settings.auth_configured:
        raise _not_configured()

    if not check_credentials(
        credentials.username, credentials.password,
        settings.auth_username, settings.auth_password_hash,
    ):
        raise _unauthorized("Incorrect username or password")

    token, expires_at = create_token(
        settings.auth_username, settings.auth_secret_key, settings.auth_token_ttl_minutes * 60
    )
    return {"access_token": token, "expires_at": expires_at, "username": settings.auth_username}


@router.get("/me")
def me(username: str = Depends(require_auth)):
    return {"username": username}
