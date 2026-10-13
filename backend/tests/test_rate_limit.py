"""Rate limiting: sliding window, per-route buckets and client IP resolution."""
import pytest
from starlette.requests import Request

from app.rate_limit import SlidingWindowLimiter, client_ip
from tests.conftest import TEST_PASSWORD, TEST_USERNAME, auth_headers

CSV = b"username,age_days,followers,following,posts_per_day,profile_completeness,avg_likes,avg_comments\n"


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def make_request(peer="10.0.0.1", forwarded=None):
    headers = [(b"x-forwarded-for", forwarded.encode())] if forwarded else []
    return Request({"type": "http", "headers": headers, "client": (peer, 1234)})


# --- Limiter ------------------------------------------------------------------

def test_sliding_window_blocks_then_recovers():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(clock=clock)
    assert [limiter.hit("k", 3) for _ in range(3)] == [0.0, 0.0, 0.0]
    assert limiter.hit("k", 3) == pytest.approx(60.0)

    clock.now += 30
    assert limiter.hit("k", 3) == pytest.approx(30.0)
    clock.now += 30.001
    assert limiter.hit("k", 3) == 0.0


def test_keys_are_independent():
    limiter = SlidingWindowLimiter(clock=FakeClock())
    assert limiter.hit("a", 1) == 0.0
    assert limiter.hit("a", 1) > 0
    assert limiter.hit("b", 1) == 0.0


def test_idle_keys_are_swept():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(clock=clock)
    for i in range(100):
        limiter.hit(f"ip-{i}", 5)
    clock.now += 61
    limiter.hit("fresh", 5)
    assert set(limiter._hits) == {"fresh"}


# --- Client IP ----------------------------------------------------------------

def test_forwarded_header_ignored_without_trusted_proxies():
    assert client_ip(make_request(forwarded="1.2.3.4"), trusted_proxy_hops=0) == "10.0.0.1"


def test_rightmost_entry_used_behind_one_proxy():
    # The client forged "6.6.6.6"; the proxy appended the real address.
    request = make_request(forwarded="6.6.6.6, 203.0.113.9")
    assert client_ip(request, trusted_proxy_hops=1) == "203.0.113.9"


def test_entry_matching_proxy_hops():
    request = make_request(forwarded="6.6.6.6, 203.0.113.9, 172.16.0.2")
    assert client_ip(request, trusted_proxy_hops=2) == "203.0.113.9"


def test_short_forwarded_header_falls_back_to_peer():
    assert client_ip(make_request(forwarded="6.6.6.6"), trusted_proxy_hops=2) == "10.0.0.1"
    assert client_ip(make_request(), trusted_proxy_hops=1) == "10.0.0.1"


# --- Endpoints ----------------------------------------------------------------

def login(client, password=TEST_PASSWORD):
    return client.post("/api/auth/login", json={"username": TEST_USERNAME, "password": password})


def test_login_attempts_are_limited(anon_client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_login_per_minute=3)
    assert [login(anon_client, "wrong password x").status_code for _ in range(3)] == [401, 401, 401]

    blocked = login(anon_client)  # even the correct password is refused now
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers["retry-after"]) <= 60


def test_api_requests_are_limited(client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_api_per_minute=5)
    statuses = [client.get("/api/dashboard/summary").status_code for _ in range(6)]
    assert statuses == [200] * 5 + [429]


def test_rate_limit_applies_before_authentication(anon_client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_api_per_minute=2)
    statuses = [anon_client.get("/api/accounts").status_code for _ in range(3)]
    assert statuses == [401, 401, 429]


def test_imports_have_a_stricter_limit(client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_import_per_minute=2, rate_limit_api_per_minute=100)
    upload = lambda: client.post("/api/import/csv", files={"file": ("a.csv", CSV, "text/csv")})  # noqa: E731
    assert [upload().status_code for _ in range(3)] == [200, 200, 429]
    assert client.get("/api/accounts").status_code == 200  # other routes unaffected


def test_public_endpoints_are_not_limited(anon_client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_api_per_minute=1)
    assert all(anon_client.get("/api/health").status_code == 200 for _ in range(5))


def test_rate_limiting_can_be_disabled(client, use_settings):
    use_settings(rate_limit_enabled=False, rate_limit_api_per_minute=1)
    assert all(client.get("/api/accounts").status_code == 200 for _ in range(5))


def test_zero_disables_a_single_limit(client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_api_per_minute=0)
    assert all(client.get("/api/accounts").status_code == 200 for _ in range(5))


def test_spoofed_forwarded_for_does_not_bypass_limit(anon_client, use_settings):
    use_settings(rate_limit_enabled=True, rate_limit_api_per_minute=2, trusted_proxy_hops=0)
    statuses = [
        anon_client.get("/api/accounts", headers={**auth_headers(), "X-Forwarded-For": f"9.9.9.{i}"}).status_code
        for i in range(3)
    ]
    assert statuses == [200, 200, 429]
