"""Regression tests for bugs fixed during the audit."""
from datetime import datetime
from pathlib import Path

from app.models import Account, Analysis

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "synthetic_accounts.csv"

CSV_HEADER = "username,age_days,followers,following,posts_per_day,profile_completeness,avg_likes,avg_comments,archetype\n"


def upload_csv(client, text, filename="accounts.csv"):
    return client.post(
        "/api/import/csv",
        files={"file": (filename, text.encode("utf-8"), "text/csv")},
    )


# --- Accounts listing -------------------------------------------------------

def test_risk_score_sort_does_not_duplicate_reanalyzed_accounts(client, make_account):
    """Sorting by risk_score used to outer-join every analysis, duplicating rows."""
    first = make_account(username="first")
    make_account(username="second")
    make_account(username="third")
    for _ in range(3):
        client.post(f"/api/accounts/{first['id']}/analyze")

    # Duplicated join rows used to fill the page, so limit=2 returned one account.
    response = client.get("/api/accounts?sort_by=risk_score&sort_order=desc&limit=2")
    assert response.status_code == 200
    data = response.json()
    ids = [a["id"] for a in data["accounts"]]
    assert len(ids) == len(set(ids)) == 2
    assert data["total"] == 3
    assert ids[0] == first["id"]
    # Unanalyzed accounts sort last when descending.
    assert data["accounts"][-1]["latest_analysis"] is None


def test_category_filter_combined_with_risk_score_sort(client, make_account):
    """category + sort_by=risk_score joined analyses twice and errored."""
    risky = make_account(
        username="risky", age_days=2, followers=5, following=4000,
        posts_per_day=60, profile_completeness=10, avg_likes=0, avg_comments=0,
    )
    safe = make_account(username="safe", age_days=900, followers=5000, following=100,
                        avg_likes=600, avg_comments=60, profile_completeness=100)
    client.post(f"/api/accounts/{risky['id']}/analyze")
    client.post(f"/api/accounts/{safe['id']}/analyze")

    response = client.get("/api/accounts?category=critical&sort_by=risk_score&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    assert [a["username"] for a in data["accounts"]] == ["risky"]
    assert data["total"] == 1


def test_category_filter_uses_latest_analysis_only(client, make_account, db_session):
    account = make_account(username="changed")
    db_session.add_all([
        Analysis(account_id=account["id"], risk_score=90, category="CRITICAL",
                 recommended_action="x", analysis_json="{}"),
        Analysis(account_id=account["id"], risk_score=10, category="LOW",
                 recommended_action="x", analysis_json="{}"),
    ])
    db_session.commit()

    assert client.get("/api/accounts?category=CRITICAL").json()["total"] == 0
    assert client.get("/api/accounts?category=LOW").json()["total"] == 1


def test_invalid_category_is_rejected(client):
    assert client.get("/api/accounts?category=bogus").status_code == 422


def test_search_treats_wildcards_literally(client, make_account):
    """'_' is a LIKE wildcard; unescaped it matched every username."""
    make_account(username="has_underscore")
    make_account(username="plainname")

    data = client.get("/api/accounts", params={"search": "_"}).json()
    assert [a["username"] for a in data["accounts"]] == ["has_underscore"]

    data = client.get("/api/accounts", params={"search": "%"}).json()
    assert data["total"] == 0


def test_get_account_handles_corrupt_analysis_json(client, make_account, db_session):
    account = make_account(username="corrupt")
    db_session.add(Analysis(account_id=account["id"], risk_score=50, category="MEDIUM",
                            recommended_action="Monitor account", analysis_json="not json"))
    db_session.commit()

    response = client.get(f"/api/accounts/{account['id']}")
    assert response.status_code == 200
    assert response.json()["latest_analysis"]["details"] is None


# --- Timestamps -------------------------------------------------------------

def test_timestamps_are_serialized_with_utc_offset(client, make_account):
    """Naive timestamps were parsed as local time by browsers."""
    account = make_account(username="tz_user")
    analyzed = client.post(f"/api/accounts/{account['id']}/analyze").json()

    for value in (account["created_at"], analyzed["timestamp"]):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        assert parsed.utcoffset() is not None
        assert parsed.utcoffset().total_seconds() == 0

    detail = client.get(f"/api/accounts/{account['id']}").json()
    assert datetime.fromisoformat(
        detail["latest_analysis"]["created_at"].replace("Z", "+00:00")
    ).utcoffset() is not None


# --- Validation -------------------------------------------------------------

def test_blank_username_is_rejected(client):
    from tests.conftest import VALID_ACCOUNT
    response = client.post("/api/analyze", json={**VALID_ACCOUNT, "username": "   "})
    assert response.status_code == 422


def test_username_is_trimmed(client, make_account):
    account = make_account(username="  padded  ")
    assert account["username"] == "padded"


def test_duplicate_username_returns_400(client, make_account):
    make_account(username="dup")
    from tests.conftest import VALID_ACCOUNT
    response = client.post("/api/accounts", json={**VALID_ACCOUNT, "username": "dup"})
    assert response.status_code == 400


def test_top_risk_limit_is_bounded(client):
    assert client.get("/api/dashboard/top-risk?limit=0").status_code == 422
    assert client.get("/api/dashboard/top-risk?limit=1000").status_code == 422
    assert client.get("/api/dashboard/top-risk?limit=5").status_code == 200


# --- Dashboard --------------------------------------------------------------

def test_dashboard_counts_only_latest_analysis(client, make_account, db_session):
    a = make_account(username="a")
    make_account(username="never_analyzed")
    db_session.add_all([
        Analysis(account_id=a["id"], risk_score=95, category="CRITICAL",
                 recommended_action="x", analysis_json="{}"),
        Analysis(account_id=a["id"], risk_score=20, category="LOW",
                 recommended_action="x", analysis_json="{}"),
    ])
    db_session.commit()

    summary = client.get("/api/dashboard/summary").json()
    assert summary == {
        "total_accounts": 2,
        "low_risk": 1,
        "medium_risk": 0,
        "high_risk": 0,
        "critical_risk": 0,
        "average_risk_score": 20.0,
    }

    distribution = client.get("/api/dashboard/distribution").json()["distribution"]
    assert distribution == [
        {"category": "LOW", "count": 1},
        {"category": "MEDIUM", "count": 0},
        {"category": "HIGH", "count": 0},
        {"category": "CRITICAL", "count": 0},
    ]

    top = client.get("/api/dashboard/top-risk").json()["accounts"]
    assert len(top) == 1 and top[0]["risk_score"] == 20


def test_dashboard_empty_database(client):
    summary = client.get("/api/dashboard/summary").json()
    assert summary["total_accounts"] == 0
    assert summary["average_risk_score"] == 0.0
    assert client.get("/api/dashboard/top-risk").json() == {"accounts": []}


# --- CSV import -------------------------------------------------------------

def test_csv_import_basic(client, db_session):
    text = CSV_HEADER + "alice,400,1000,500,2,90,80,8,NORMAL\nbob,5,10,900,40,20,0.1,0,\n"
    response = upload_csv(client, text)
    assert response.status_code == 200
    assert response.json() == {"imported": 2, "skipped": 0, "errors": []}
    bob = db_session.query(Account).filter_by(username="bob").one()
    assert bob.archetype is None


def test_csv_duplicate_usernames_within_file_do_not_abort_import(client, db_session):
    """Two rows with the same username used to raise IntegrityError -> 500."""
    text = CSV_HEADER + "dup,400,1000,500,2,90,80,8,\ndup,400,1000,500,2,90,80,8,\nother,1,1,1,1,1,1,1,\n"
    response = upload_csv(client, text)
    assert response.status_code == 200
    assert response.json()["imported"] == 2
    assert response.json()["skipped"] == 1
    assert db_session.query(Account).count() == 2


def test_csv_skips_existing_usernames(client, make_account):
    make_account(username="existing")
    response = upload_csv(client, CSV_HEADER + "existing,400,1000,500,2,90,80,8,\n")
    assert response.json() == {"imported": 0, "skipped": 1, "errors": []}


def test_csv_blank_username_is_an_error_not_nan(client, db_session):
    """pandas turned an empty username into the literal string 'nan'."""
    response = upload_csv(client, CSV_HEADER + ",400,1000,500,2,90,80,8,\n")
    data = response.json()
    assert data["imported"] == 0
    assert len(data["errors"]) == 1 and data["errors"][0].startswith("Row 2:")
    assert db_session.query(Account).filter_by(username="nan").count() == 0


def test_csv_fractional_integer_is_rejected_not_truncated(client, db_session):
    response = upload_csv(client, CSV_HEADER + "frac,12.7,1000,500,2,90,80,8,\n")
    assert response.json()["imported"] == 0
    assert "age_days" in response.json()["errors"][0]


def test_csv_rejects_non_finite_numbers(client):
    response = upload_csv(client, CSV_HEADER + "inf_user,10,10,10,inf,90,80,8,\n")
    assert response.json()["imported"] == 0
    assert "posts_per_day" in response.json()["errors"][0]


def test_csv_missing_columns(client):
    response = upload_csv(client, "username,age_days\nx,1\n")
    assert response.status_code == 400
    assert "followers" in response.json()["detail"]


def test_csv_wrong_extension_and_encoding(client):
    assert upload_csv(client, CSV_HEADER, filename="data.txt").status_code == 400
    response = client.post(
        "/api/import/csv",
        files={"file": ("bad.csv", b"\xff\xfe\x00bad", "text/csv")},
    )
    assert response.status_code == 400


def test_csv_too_large(client, monkeypatch):
    from app.routes import import_data
    monkeypatch.setattr(import_data, "MAX_UPLOAD_BYTES", 100)
    response = upload_csv(client, CSV_HEADER + "x,1,1,1,1,1,1,1,\n" * 10)
    assert response.status_code == 413


def test_csv_handles_bom_and_blank_lines(client):
    text = "﻿" + CSV_HEADER + "\nbom_user,400,1000,500,2,90,80,8,\n\n"
    response = upload_csv(client, text)
    assert response.json() == {"imported": 1, "skipped": 0, "errors": []}


def test_csv_import_stores_initial_analysis(client, db_session):
    """Imported accounts were never analyzed, leaving the dashboard empty."""
    text = CSV_HEADER + "fresh,400,1000,500,2,90,80,8,\nbotty,2,5,4000,60,10,0,0,\n"
    assert upload_csv(client, text).json()["imported"] == 2

    assert db_session.query(Analysis).count() == 2
    summary = client.get("/api/dashboard/summary").json()
    assert summary["low_risk"] + summary["medium_risk"] + summary["high_risk"] + summary["critical_risk"] == 2
    assert summary["critical_risk"] == 1

    botty = client.get("/api/accounts", params={"search": "botty"}).json()["accounts"][0]
    assert botty["latest_analysis"]["category"] == "CRITICAL"


def test_bundled_synthetic_dataset_imports_cleanly(client):
    """The shipped demo dataset must import without validation errors."""
    response = upload_csv(client, DATA_FILE.read_text(encoding="utf-8"))
    assert response.status_code == 200
    data = response.json()
    assert data["errors"] == []
    assert data["imported"] == sum(1 for _ in DATA_FILE.open(encoding="utf-8")) - 1

    summary = client.get("/api/dashboard/summary").json()
    analyzed = sum(summary[k] for k in ("low_risk", "medium_risk", "high_risk", "critical_risk"))
    assert analyzed == data["imported"]


# --- Analysis history -------------------------------------------------------

def test_analysis_history_is_newest_first(client, make_account):
    account = make_account(username="history")
    for _ in range(2):
        client.post(f"/api/accounts/{account['id']}/analyze")

    data = client.get(f"/api/accounts/{account['id']}/analysis").json()
    ids = [a["id"] for a in data["analyses"]]
    assert len(ids) == 2 and ids == sorted(ids, reverse=True)
    assert client.get("/api/accounts/9999/analysis").status_code == 404


# --- CORS -------------------------------------------------------------------

def test_cors_origin_parsing():
    from app.main import parse_cors_origins
    assert parse_cors_origins(" https://a.example/ , ,http://localhost:5173") == [
        "https://a.example",
        "http://localhost:5173",
    ]


def test_cors_does_not_allow_credentials(client):
    response = client.options(
        "/api/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-credentials" not in response.headers
