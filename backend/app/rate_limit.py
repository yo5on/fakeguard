"""
In-memory sliding-window rate limiting.

State lives in this process, so limits apply per worker. That matches the
documented deployment (one uvicorn worker); with several workers or
instances, each enforces its own window and a shared store (e.g. Redis)
would be needed for a global limit.
"""
import math
import threading
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from fastapi import Depends, HTTPException, Request

from .config import Settings, get_settings

WINDOW_SECONDS = 60.0


class SlidingWindowLimiter:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_sweep = clock()

    def hit(self, key: str, limit: int, window: float = WINDOW_SECONDS) -> float:
        """
        Record a request for ``key``. Returns 0 if allowed, otherwise the
        number of seconds until the oldest request leaves the window.
        """
        now = self._clock()
        with self._lock:
            self._sweep(now, window)
            hits = self._hits[key]
            while hits and hits[0] <= now - window:
                hits.popleft()
            if len(hits) >= limit:
                return max(0.0, hits[0] + window - now)
            hits.append(now)
            return 0.0

    def _sweep(self, now: float, window: float) -> None:
        # Drop idle keys periodically so memory doesn't grow with every IP seen.
        if now - self._last_sweep < window:
            return
        self._last_sweep = now
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= now - window]:
            del self._hits[key]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip(request: Request, trusted_proxy_hops: int) -> str:
    """
    Resolve the client address. X-Forwarded-For is only used when the app is
    told how many proxies sit in front of it: each proxy appends the address
    it received the request from, so the entry ``trusted_proxy_hops`` places
    from the right was written by our outermost proxy and cannot be forged
    by the client (entries further left can be).
    """
    peer = request.client.host if request.client else "unknown"
    if trusted_proxy_hops <= 0:
        return peer
    forwarded = [part.strip() for part in request.headers.get("x-forwarded-for", "").split(",") if part.strip()]
    if len(forwarded) >= trusted_proxy_hops:
        return forwarded[-trusted_proxy_hops]
    # Fewer entries than expected proxies: the header is not trustworthy.
    return peer


def rate_limit(bucket: str, limit_setting: str):
    """Dependency enforcing ``Settings.<limit_setting>`` requests/minute per client IP."""

    def dependency(request: Request, settings: Settings = Depends(get_settings)) -> None:
        limit = getattr(settings, limit_setting)
        if not settings.rate_limit_enabled or limit <= 0:
            return
        key = f"{bucket}:{client_ip(request, settings.trusted_proxy_hops)}"
        retry_after = limiter.hit(key, limit)
        if retry_after:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down and try again shortly.",
                headers={"Retry-After": str(max(1, math.ceil(retry_after)))},
            )

    return dependency
