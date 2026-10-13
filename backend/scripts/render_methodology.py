"""
Regenerate the scoring tables in docs/scoring-methodology.md from
app/scoring/thresholds.py, the single source of truth for scoring rules.

    python scripts/render_methodology.py          # rewrite the tables
    python scripts/render_methodology.py --check  # exit 1 if they are stale

Each table lives between ``<!-- BEGIN GENERATED: name -->`` and
``<!-- END GENERATED: name -->`` markers; text outside the markers is
left untouched. A backend test runs the check so the doc cannot drift.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.scoring import thresholds as t  # noqa: E402

DOC = Path(__file__).resolve().parents[2] / "docs" / "scoring-methodology.md"

_BLOCK = re.compile(
    r"(<!-- BEGIN GENERATED: (?P<name>[a-z_]+) -->)(?P<body>.*?)(<!-- END GENERATED: (?P=name) -->)",
    re.S,
)


def _fmt(value: float) -> str:
    return f"{value:g}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


def render_blocks() -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    blocks["weights"] = _table(
        ["Feature", "Weight"],
        [[t.FEATURE_LABELS[k], f"{w * 100:g}%"] for k, w in t.FEATURE_WEIGHTS.items()],
    )
    for key, feature in t.BANDED_FEATURES.items():
        blocks[key] = _table(["Range", "Risk Score"], [[label, _fmt(risk)] for label, risk in feature.bands()])
    blocks["categories"] = _table(
        ["Category", "Score Range", "Recommended Action"],
        [[name, info["range"], info["action"]] for name, info in t.category_ranges().items()],
    )
    blocks["reason_codes"] = _table(
        ["Code", "Description", "Trigger"],
        [[r.code, r.description, t.reason_code_trigger(r)] for r in t.REASON_CODE_RULES],
    )
    return blocks


def render(text: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    blocks = render_blocks()
    seen = set()

    def replace(match: re.Match) -> str:
        name = match.group("name")
        if name not in blocks:
            raise SystemExit(f"Unknown generated block: {name}")
        seen.add(name)
        body = newline.join(blocks[name])
        return f"{match.group(1)}{newline}{body}{newline}{match.group(4)}"

    result = _BLOCK.sub(replace, text)
    missing = set(blocks) - seen
    if missing:
        raise SystemExit(f"{DOC.name} is missing generated blocks: {', '.join(sorted(missing))}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if the document is out of date")
    args = parser.parse_args(argv)

    current = DOC.read_bytes().decode("utf-8")
    updated = render(current)
    if args.check:
        if updated != current:
            print(f"{DOC} is out of date; run python scripts/render_methodology.py", file=sys.stderr)
            return 1
        print(f"{DOC.name} is up to date.")
        return 0
    DOC.write_bytes(updated.encode("utf-8"))
    print(f"Updated {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
