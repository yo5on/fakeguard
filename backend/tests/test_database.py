"""Database URL handling and the SQLite -> PostgreSQL migration script."""
import importlib.util
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import init_db, make_engine, normalize_database_url
from app.models import Account, Analysis

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "migrate_database.py"
_spec = importlib.util.spec_from_file_location("migrate_database", SCRIPT)
migrate_database = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate_database)

POSTGRES_URL = os.getenv("FAKEGUARD_TEST_POSTGRES_URL")


@pytest.mark.parametrize("url,expected", [
    ("postgres://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
    ("postgresql+psycopg://u@h/db", "postgresql+psycopg://u@h/db"),
    (" sqlite:///./fakeguard.db ", "sqlite:///./fakeguard.db"),
    ("sqlite:////var/data/fakeguard.db", "sqlite:////var/data/fakeguard.db"),
])
def test_normalize_database_url(url, expected):
    assert normalize_database_url(url) == expected


def seed(url: str, accounts: int = 3) -> None:
    engine = make_engine(url)
    init_db(bind=engine)
    created = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    with Session(engine) as db:
        for i in range(accounts):
            account = Account(
                id=10 + i * 5,  # non-contiguous ids must survive the copy
                username=f"seed_{i}", age_days=i, followers=i * 10, following=5,
                posts_per_day=1.5, profile_completeness=50, avg_likes=1, avg_comments=0,
                archetype="NORMAL" if i else None, created_at=created, updated_at=created,
            )
            account.analyses.append(Analysis(
                risk_score=40.0 + i, category="MEDIUM", recommended_action="Monitor account",
                analysis_json='{"k": 1}', created_at=created,
            ))
            db.add(account)
        db.commit()
    engine.dispose()


def snapshot(url: str):
    engine = make_engine(url)
    with Session(engine) as db:
        accounts = [
            (a.id, a.username, a.followers, a.archetype, a.created_at)
            for a in db.scalars(select(Account).order_by(Account.id))
        ]
        analyses = [
            (a.id, a.account_id, a.risk_score, a.analysis_json, a.created_at)
            for a in db.scalars(select(Analysis).order_by(Analysis.id))
        ]
    engine.dispose()
    return accounts, analyses


def test_migration_copies_everything_and_leaves_source_untouched(tmp_path):
    source = f"sqlite:///{tmp_path / 'source.db'}"
    target = f"sqlite:///{tmp_path / 'target.db'}"
    seed(source)
    before = snapshot(source)

    assert migrate_database.migrate(source, target) == {"accounts": 3, "analyses": 3}

    assert snapshot(source) == before
    assert snapshot(target) == before


def test_migration_refuses_non_empty_target(tmp_path):
    source = f"sqlite:///{tmp_path / 'source.db'}"
    target = f"sqlite:///{tmp_path / 'target.db'}"
    seed(source)
    seed(target, accounts=1)
    target_before = snapshot(target)

    with pytest.raises(SystemExit, match="already contains data"):
        migrate_database.migrate(source, target)
    assert snapshot(target) == target_before


def test_migration_dry_run_writes_nothing(tmp_path):
    source = f"sqlite:///{tmp_path / 'source.db'}"
    target_path = tmp_path / "target.db"
    seed(source)
    migrate_database.migrate(source, f"sqlite:///{target_path}", dry_run=True)
    assert not target_path.exists()


def test_migration_rejects_same_database(tmp_path):
    url = f"sqlite:///{tmp_path / 'same.db'}"
    with pytest.raises(SystemExit, match="same database"):
        migrate_database.migrate(url, url)


def test_migration_requires_source_tables(tmp_path):
    with pytest.raises(SystemExit, match="nothing to migrate"):
        migrate_database.migrate(f"sqlite:///{tmp_path / 'empty.db'}", f"sqlite:///{tmp_path / 't.db'}")


def test_redact_hides_passwords():
    assert "secret" not in migrate_database.redact("postgres://user:secret@host/db")


@pytest.mark.skipif(not POSTGRES_URL, reason="set FAKEGUARD_TEST_POSTGRES_URL to run against PostgreSQL")
def test_migration_into_postgres_and_sequence_reset(tmp_path):
    """Requires an existing PostgreSQL server; a throwaway database is created and dropped."""
    import psycopg
    from sqlalchemy.engine.url import make_url

    admin = make_url(normalize_database_url(POSTGRES_URL))
    name = f"fakeguard_test_{uuid.uuid4().hex[:8]}"
    conninfo = admin.set(drivername="postgresql").render_as_string(hide_password=False)
    with psycopg.connect(conninfo, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{name}"')
    target = admin.set(database=name).render_as_string(hide_password=False)
    try:
        source = f"sqlite:///{tmp_path / 'source.db'}"
        seed(source)
        migrate_database.migrate(source, target)
        assert snapshot(target) == snapshot(source)

        # New rows must get ids above the copied ones.
        engine = make_engine(target)
        with Session(engine) as db:
            account = Account(username="after_migration", age_days=1, followers=1, following=1,
                              posts_per_day=1, profile_completeness=1, avg_likes=1, avg_comments=1)
            db.add(account)
            db.commit()
            assert account.id == 21  # max copied id was 20
        engine.dispose()
    finally:
        with psycopg.connect(conninfo, autocommit=True) as conn:
            conn.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
