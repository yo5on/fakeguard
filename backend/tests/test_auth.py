"""Authentication: password hashing, tokens, login and route protection."""
import time

import pytest

from app.config import Settings, load_settings
from app.security import (
    check_credentials,
    create_token,
    decode_token,
    hash_password,
    is_valid_password_hash,
    verify_password,
)
from tests.conftest import (
    TEST_PASSWORD,
    TEST_SECRET,
    TEST_USERNAME,
    VALID_ACCOUNT,
    auth_headers,
)

# Every route that exposes account data, runs analyses or writes data.
PROTECTED_ROUTES = [
    ("get", "/api/accounts"),
    ("get", "/api/accounts/1"),
    ("post", "/api/accounts"),
    ("post", "/api/analyze"),
    ("post", "/api/accounts/1/analyze"),
    ("get", "/api/accounts/1/analysis"),
    ("get", "/api/dashboard/summary"),
    ("get", "/api/dashboard/distribution"),
    ("get", "/api/dashboard/top-risk"),
    ("post", "/api/import/csv"),
    ("get", "/api/auth/me"),
]

PUBLIC_ROUTES = ["/api/health", "/api/config/scoring", "/api/auth/status"]


def call(client, method, path, **kwargs):
    return getattr(client, method)(path, **kwargs)


# --- Password hashing ---------------------------------------------------------

def test_password_hash_roundtrip():
    stored = hash_password("a long enough password")
    assert stored.startswith("scrypt$")
    assert is_valid_password_hash(stored)
    assert verify_password("a long enough password", stored)
    assert not verify_password("a long enough passworD", stored)


def test_password_hashes_are_salted():
    assert hash_password("same password here") != hash_password("same password here")


def test_short_passwords_are_rejected():
    with pytest.raises(ValueError):
        hash_password("short")


@pytest.mark.parametrize("bad", ["", "plaintext-password", "scrypt$1$2$3$x", "bcrypt$a$b$c$d$e", "scrypt$x$8$1$c2FsdA$aGFzaA"])
def test_malformed_hashes_never_verify(bad):
    assert not is_valid_password_hash(bad)
    assert not verify_password("anything", bad)


def test_check_credentials_requires_both_parts():
    stored = hash_password(TEST_PASSWORD)
    assert check_credentials(TEST_USERNAME, TEST_PASSWORD, TEST_USERNAME, stored)
    assert not check_credentials("someone", TEST_PASSWORD, TEST_USERNAME, stored)
    assert not check_credentials(TEST_USERNAME, "wrong password!!", TEST_USERNAME, stored)


# --- Tokens -------------------------------------------------------------------

def test_token_roundtrip_and_expiry():
    token, exp = create_token("alice", TEST_SECRET, 60, now=1_000)
    assert exp == 1_060
    assert decode_token(token, TEST_SECRET, now=1_030)["sub"] == "alice"
    assert decode_token(token, TEST_SECRET, now=1_060) is None


def test_tampered_or_foreign_tokens_are_rejected():
    token, _ = create_token("alice", TEST_SECRET, 60)
    payload, signature = token.split(".")
    forged_payload, _ = create_token("admin", TEST_SECRET + "x", 60)

    assert decode_token(token, "another-secret-key-of-sufficient-length!!") is None
    assert decode_token(f"{forged_payload.split('.')[0]}.{signature}", TEST_SECRET) is None
    assert decode_token(f"{payload}.{signature[:-2]}AA", TEST_SECRET) is None
    for junk in ["", "abc", "a.b.c", "....", "%%%.%%%"]:
        assert decode_token(junk, TEST_SECRET) is None


# --- Login --------------------------------------------------------------------

def test_login_success_returns_working_token(anon_client):
    response = anon_client.post("/api/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["username"] == TEST_USERNAME
    assert body["expires_at"] > time.time()

    me = anon_client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json() == {"username": TEST_USERNAME}


@pytest.mark.parametrize("username,password", [
    (TEST_USERNAME, "wrong password value"),
    ("intruder", TEST_PASSWORD),
    (TEST_USERNAME.upper(), TEST_PASSWORD),
])
def test_login_failures_are_uniform(anon_client, username, password):
    response = anon_client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_validates_payload(anon_client):
    assert anon_client.post("/api/auth/login", json={"username": "", "password": "x"}).status_code == 422
    assert anon_client.post("/api/auth/login", json={}).status_code == 422


def test_token_ttl_comes_from_settings(anon_client, use_settings):
    use_settings(auth_token_ttl_minutes=5)
    body = anon_client.post("/api/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD}).json()
    assert body["expires_at"] - time.time() == pytest.approx(300, abs=5)


# --- Route protection ---------------------------------------------------------

@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
def test_protected_routes_require_a_token(anon_client, method, path):
    response = call(anon_client, method, path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("header", [
    "Bearer not-a-token",
    "Basic cmV2aWV3ZXI6cGFzcw==",
    "Bearer ",
    "Token abc.def",
])
def test_invalid_authorization_headers_are_rejected(anon_client, header):
    assert anon_client.get("/api/accounts", headers={"Authorization": header}).status_code == 401


def test_expired_token_is_rejected(anon_client):
    token, _ = create_token(TEST_USERNAME, TEST_SECRET, 60, now=time.time() - 120)
    response = anon_client.get("/api/accounts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_token_for_another_subject_is_rejected(anon_client):
    assert anon_client.get("/api/accounts", headers=auth_headers(subject="someone-else")).status_code == 401


def test_rotating_the_secret_invalidates_tokens(anon_client, use_settings):
    headers = auth_headers()
    assert anon_client.get("/api/accounts", headers=headers).status_code == 200
    use_settings(auth_secret_key="a-brand-new-secret-key-0123456789-abcdef")
    assert anon_client.get("/api/accounts", headers=headers).status_code == 401


@pytest.mark.parametrize("path", PUBLIC_ROUTES)
def test_public_routes_need_no_token(anon_client, path):
    assert anon_client.get(path).status_code == 200


def test_auth_status(anon_client, use_settings):
    assert anon_client.get("/api/auth/status").json() == {"auth_required": True, "auth_configured": True}
    use_settings(auth_disabled=True)
    assert anon_client.get("/api/auth/status").json() == {"auth_required": False, "auth_configured": False}


# --- Fail-closed configuration ------------------------------------------------

@pytest.mark.parametrize("overrides", [
    {"auth_username": None},
    {"auth_password_hash": None},
    {"auth_password_hash": "plaintext-password-in-env"},
    {"auth_secret_key": None},
    {"auth_secret_key": "too-short"},
])
@pytest.mark.parametrize("method,path", [("get", "/api/accounts"), ("post", "/api/import/csv"), ("post", "/api/analyze")])
def test_unconfigured_auth_fails_closed(anon_client, use_settings, overrides, method, path):
    use_settings(**overrides)
    response = call(anon_client, method, path, headers=auth_headers())
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_login_fails_closed_when_unconfigured(anon_client, use_settings):
    use_settings(auth_secret_key=None)
    response = anon_client.post("/api/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 503


def test_health_stays_up_when_auth_unconfigured(anon_client, use_settings):
    use_settings(auth_username=None)
    assert anon_client.get("/api/health").status_code == 200


def test_explicitly_disabled_auth_allows_anonymous_access(anon_client, use_settings):
    use_settings(auth_disabled=True, auth_username=None, auth_password_hash=None, auth_secret_key=None)
    assert anon_client.post("/api/accounts", json=VALID_ACCOUNT).status_code == 201
    assert anon_client.get("/api/accounts").status_code == 200
    assert anon_client.get("/api/auth/me").json() == {"username": "anonymous"}
    assert anon_client.post("/api/auth/login", json={"username": "a", "password": "b"}).status_code == 400


# --- Environment parsing ------------------------------------------------------

def test_settings_default_to_auth_required_and_unconfigured(monkeypatch):
    for name in ["AUTH_DISABLED", "AUTH_USERNAME", "AUTH_PASSWORD_HASH", "AUTH_SECRET_KEY"]:
        monkeypatch.delenv(name, raising=False)
    settings = load_settings()
    assert settings.auth_disabled is False
    assert settings.auth_configured is False
    assert len(settings.auth_problems()) == 3


def test_settings_from_environment(monkeypatch):
    stored = hash_password(TEST_PASSWORD)
    monkeypatch.setenv("AUTH_USERNAME", " reviewer ")
    monkeypatch.setenv("AUTH_PASSWORD_HASH", stored)
    monkeypatch.setenv("AUTH_SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("AUTH_TOKEN_TTL_MINUTES", "30")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_PER_MINUTE", "3")
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "1")
    settings = load_settings()
    assert settings.auth_configured
    assert settings.auth_username == "reviewer"
    assert settings.auth_token_ttl_minutes == 30
    assert settings.rate_limit_login_per_minute == 3
    assert settings.trusted_proxy_hops == 1


@pytest.mark.parametrize("name,value", [("AUTH_TOKEN_TTL_MINUTES", "0"), ("RATE_LIMIT_API_PER_MINUTE", "lots")])
def test_invalid_numeric_settings_raise(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(RuntimeError, match=name):
        load_settings()


def test_disabled_flag_overrides_configuration():
    settings = Settings(auth_disabled=True, auth_username="x", auth_password_hash=hash_password(TEST_PASSWORD),
                        auth_secret_key=TEST_SECRET)
    assert settings.auth_configured is False
    assert settings.auth_problems() == []


def test_cors_preflight_allows_authorization_header(anon_client):
    response = anon_client.options(
        "/api/accounts",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
