"""
Password hashing and stateless bearer tokens, using only the standard library.

Passwords: scrypt, stored as ``scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64>``.
Tokens: ``<payload_b64>.<signature_b64>`` where the payload is JSON with
``sub``, ``iat`` and ``exp`` and the signature is HMAC-SHA256 over the
payload using AUTH_SECRET_KEY. Rotating the key invalidates every token.
"""
import base64
import binascii
import getpass
import hashlib
import hmac
import json
import secrets
import sys
import time
from typing import Optional

SCRYPT_N = 2 ** 15
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 12
# scrypt needs ~128 * n * r bytes; leave headroom for the stored parameters.
_SCRYPT_MAXMEM = 256 * 1024 * 1024


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def hash_password(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
        dklen=SCRYPT_DKLEN, maxmem=_SCRYPT_MAXMEM,
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, n, r, p, salt_b64, hash_b64 = stored_hash.split("$")
        if scheme != "scrypt":
            return False
        salt, expected = _b64decode(salt_b64), _b64decode(hash_b64)
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p),
            dklen=len(expected), maxmem=_SCRYPT_MAXMEM,
        )
    except (ValueError, TypeError, binascii.Error):
        return False
    return hmac.compare_digest(digest, expected)


def is_valid_password_hash(stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        return False
    try:
        int(parts[1]), int(parts[2]), int(parts[3])
        _b64decode(parts[4]), _b64decode(parts[5])
    except (ValueError, binascii.Error):
        return False
    return True


# A real hash of a random password, so failed logins for unknown usernames
# cost the same scrypt work as wrong passwords (no username timing oracle).
_DUMMY_HASH = hash_password(secrets.token_urlsafe(24))


def check_credentials(username: str, password: str, expected_username: str, password_hash: str) -> bool:
    username_ok = hmac.compare_digest(username.encode("utf-8"), expected_username.encode("utf-8"))
    password_ok = verify_password(password, password_hash if username_ok else _DUMMY_HASH)
    return username_ok and password_ok


def _sign(payload_b64: str, secret_key: str) -> str:
    mac = hmac.new(secret_key.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256)
    return _b64encode(mac.digest())


def create_token(subject: str, secret_key: str, ttl_seconds: int, now: Optional[float] = None) -> tuple[str, int]:
    issued_at = int(now if now is not None else time.time())
    expires_at = issued_at + ttl_seconds
    payload = json.dumps({"sub": subject, "iat": issued_at, "exp": expires_at}, separators=(",", ":"))
    payload_b64 = _b64encode(payload.encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64, secret_key)}", expires_at


def decode_token(token: str, secret_key: str, now: Optional[float] = None) -> Optional[dict]:
    """Return the token payload if the signature is valid and it has not expired."""
    try:
        payload_b64, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(signature, _sign(payload_b64, secret_key)):
        return None
    try:
        payload = json.loads(_b64decode(payload_b64))
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("sub"), str):
        return None
    exp = payload.get("exp")
    current = now if now is not None else time.time()
    if not isinstance(exp, int) or exp <= current:
        return None
    return payload


def _cli(argv: list[str]) -> int:
    usage = "usage: python -m app.security [hash-password | generate-secret]"
    if len(argv) != 1:
        print(usage, file=sys.stderr)
        return 2
    if argv[0] == "generate-secret":
        print(secrets.token_urlsafe(48))
        return 0
    if argv[0] == "hash-password":
        password = getpass.getpass("Password: ")
        if password != getpass.getpass("Repeat password: "):
            print("Passwords do not match.", file=sys.stderr)
            return 1
        try:
            print(hash_password(password))
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
        return 0
    print(usage, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
