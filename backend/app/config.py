"""
Runtime configuration read from environment variables (and an optional .env).

Settings are resolved once per process through ``get_settings()``; route
dependencies take it via ``Depends(get_settings)`` so tests can override it.
"""
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

from .security import is_valid_password_hash

load_dotenv()

logger = logging.getLogger("fakeguard.config")

MIN_SECRET_KEY_LENGTH = 32

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in _TRUE_VALUES


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(f"{name} must be an integer, got {raw!r}")
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}, got {value}")
    return value


@dataclass(frozen=True)
class Settings:
    # Authentication
    auth_disabled: bool = False
    auth_username: Optional[str] = None
    auth_password_hash: Optional[str] = None
    auth_secret_key: Optional[str] = None
    auth_token_ttl_minutes: int = 480

    # Rate limiting (requests per minute per client IP; 0 disables a limit)
    rate_limit_enabled: bool = True
    rate_limit_login_per_minute: int = 5
    rate_limit_api_per_minute: int = 120
    rate_limit_import_per_minute: int = 10
    # Number of reverse proxies in front of the app that append to
    # X-Forwarded-For. 0 = use the TCP peer address (never trust the header).
    trusted_proxy_hops: int = 0

    @property
    def auth_configured(self) -> bool:
        return not self.auth_disabled and not self.auth_problems()

    def auth_problems(self) -> list[str]:
        """Human-readable reasons why authentication is not usable."""
        if self.auth_disabled:
            return []
        problems = []
        if not self.auth_username:
            problems.append("AUTH_USERNAME is not set")
        if not self.auth_password_hash:
            problems.append("AUTH_PASSWORD_HASH is not set")
        elif not is_valid_password_hash(self.auth_password_hash):
            problems.append("AUTH_PASSWORD_HASH is not a valid scrypt hash (see `python -m app.security hash-password`)")
        if not self.auth_secret_key:
            problems.append("AUTH_SECRET_KEY is not set")
        elif len(self.auth_secret_key) < MIN_SECRET_KEY_LENGTH:
            problems.append(f"AUTH_SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters")
        return problems


def load_settings() -> Settings:
    return Settings(
        auth_disabled=_env_bool("AUTH_DISABLED"),
        auth_username=(os.getenv("AUTH_USERNAME") or "").strip() or None,
        auth_password_hash=(os.getenv("AUTH_PASSWORD_HASH") or "").strip() or None,
        auth_secret_key=os.getenv("AUTH_SECRET_KEY") or None,
        auth_token_ttl_minutes=_env_int("AUTH_TOKEN_TTL_MINUTES", 480, minimum=1),
        rate_limit_enabled=_env_bool("RATE_LIMIT_ENABLED", True),
        rate_limit_login_per_minute=_env_int("RATE_LIMIT_LOGIN_PER_MINUTE", 5),
        rate_limit_api_per_minute=_env_int("RATE_LIMIT_API_PER_MINUTE", 120),
        rate_limit_import_per_minute=_env_int("RATE_LIMIT_IMPORT_PER_MINUTE", 10),
        trusted_proxy_hops=_env_int("TRUSTED_PROXY_HOPS", 0),
    )


@lru_cache
def get_settings() -> Settings:
    return load_settings()


def log_startup_warnings(settings: Settings) -> None:
    if settings.auth_disabled:
        logger.warning(
            "AUTH_DISABLED=true: the API is open to anyone who can reach it. "
            "Use this only for local development."
        )
    elif not settings.auth_configured:
        logger.error(
            "Authentication is not configured (%s). Protected endpoints will "
            "return 503 until it is. See README 'Authentication'.",
            "; ".join(settings.auth_problems()),
        )
    if not settings.rate_limit_enabled:
        logger.warning("RATE_LIMIT_ENABLED=false: rate limiting is off.")
