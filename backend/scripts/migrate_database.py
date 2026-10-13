"""
Copy FakeGuard data from one database to another (e.g. SQLite -> PostgreSQL).

    python scripts/migrate_database.py --source sqlite:///./fakeguard.db \
        --target "postgresql://user:pass@host:5432/dbname"

Safety properties:
- The source is only read; nothing in it is modified or deleted.
- The target schema is created if missing. The copy is refused if the target
  already contains any accounts or analyses, so existing data is never
  overwritten or merged.
- Everything is copied in one transaction: on any error nothing is committed.
- Primary keys are preserved (analysis -> account links stay intact) and
  PostgreSQL id sequences are advanced past the copied ids.
- Row counts and id sets are compared after the copy.

Pass --dry-run to report what would be copied without writing anything.
"""
import argparse
import sys
from pathlib import Path

from sqlalchemy import func, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, make_engine, normalize_database_url  # noqa: E402
from app.models import Account, Analysis  # noqa: E402

TABLES = [Account.__table__, Analysis.__table__]  # parents before children
BATCH_SIZE = 1000


def redact(url: str) -> str:
    return make_url(normalize_database_url(url)).render_as_string(hide_password=True)


def count_rows(engine: Engine) -> dict:
    with engine.connect() as conn:
        return {t.name: conn.execute(select(func.count()).select_from(t)).scalar_one() for t in TABLES}


def ids(engine: Engine, table) -> set:
    with engine.connect() as conn:
        return set(conn.execute(select(table.c.id)).scalars())


def reset_postgres_sequences(conn) -> None:
    for table in TABLES:
        conn.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {table.name}), 0) + 1, false)"
        ))


def migrate(source_url: str, target_url: str, dry_run: bool = False) -> dict:
    if normalize_database_url(source_url) == normalize_database_url(target_url):
        raise SystemExit("Source and target are the same database.")

    source = make_engine(source_url)
    target = make_engine(target_url)

    source_tables = inspect(source)
    missing = [t.name for t in TABLES if not source_tables.has_table(t.name)]
    if missing:
        raise SystemExit(f"Source database has no {', '.join(missing)} table(s); nothing to migrate.")

    source_counts = count_rows(source)
    print(f"Source {redact(source_url)}: {source_counts}")

    if dry_run:
        print("Dry run: no changes made.")
        return source_counts

    init_db(bind=target)
    target_counts = count_rows(target)
    if any(target_counts.values()):
        raise SystemExit(
            f"Target {redact(target_url)} already contains data {target_counts}; refusing to "
            "overwrite or merge. Use an empty database."
        )

    with source.connect() as src, target.begin() as dst:
        for table in TABLES:
            result = src.execute(select(table).order_by(table.c.id))
            while True:
                rows = result.mappings().fetchmany(BATCH_SIZE)
                if not rows:
                    break
                dst.execute(table.insert(), [dict(row) for row in rows])
        if target.dialect.name == "postgresql":
            reset_postgres_sequences(dst)

    copied = count_rows(target)
    if copied != source_counts:
        raise SystemExit(f"Row count mismatch after copy: source {source_counts}, target {copied}")
    for table in TABLES:
        if ids(source, table) != ids(target, table):
            raise SystemExit(f"Id mismatch in table {table.name} after copy")

    print(f"Copied to {redact(target_url)}: {copied}. Verified counts and ids.")
    return copied


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Source database URL (read-only)")
    parser.add_argument("--target", required=True, help="Empty target database URL")
    parser.add_argument("--dry-run", action="store_true", help="Only report source row counts")
    args = parser.parse_args(argv)
    migrate(args.source, args.target, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
