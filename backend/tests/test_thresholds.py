"""
Scoring thresholds have a single source of truth (app/scoring/thresholds.py).

These tests pin the current band boundaries and prove the engine and the
/api/config/scoring methodology are derived from the same tables.
"""
import dataclasses
import re

import pytest

from app.scoring import thresholds
from app.scoring.feature_rules import (
    calculate_account_age_risk,
    calculate_engagement_risk,
    calculate_follower_ratio_risk,
    calculate_posting_frequency_risk,
)
from app.scoring.reason_codes import get_reason_codes
from app.scoring.risk_engine import analyze_account, get_recommended_action, get_risk_category

# --- Exact boundary behavior (regression pins) ---------------------------------

@pytest.mark.parametrize("age,risk", [
    (0, 90), (6, 90), (7, 70), (29, 70), (30, 45), (89, 45), (90, 25),
    (179, 25), (180, 10), (365, 10), (366, 0), (5000, 0),
])
def test_account_age_boundaries(age, risk):
    assert calculate_account_age_risk(age) == risk


@pytest.mark.parametrize("followers,following,risk", [
    (49, 1000, 90), (50, 1000, 70), (199, 1000, 70), (200, 1000, 40),
    (499, 1000, 40), (500, 1000, 20), (999, 1000, 20), (1000, 1000, 0), (5, 1, 0),
])
def test_follower_ratio_boundaries(followers, following, risk):
    assert calculate_follower_ratio_risk(followers, following) == (risk, True)


@pytest.mark.parametrize("posts,risk", [
    (0, 0), (5, 0), (5.01, 20), (10, 20), (10.01, 40), (20, 40), (20.01, 70), (50, 70), (50.01, 90),
])
def test_posting_frequency_boundaries(posts, risk):
    assert calculate_posting_frequency_risk(posts) == risk


@pytest.mark.parametrize("likes,risk", [
    (0, 90), (0.49, 90), (0.5, 70), (1.99, 70), (2, 40), (4.99, 40), (5, 20), (9.99, 20), (10, 0),
])
def test_engagement_boundaries(likes, risk):
    # 100 followers, so avg_likes equals the engagement percentage.
    assert calculate_engagement_risk(likes, 0, 100) == (risk, True)


@pytest.mark.parametrize("score,category", [
    (0, "LOW"), (29.999, "LOW"), (30, "MEDIUM"), (59.999, "MEDIUM"),
    (60, "HIGH"), (79.999, "HIGH"), (80, "CRITICAL"), (100, "CRITICAL"),
])
def test_category_boundaries(score, category):
    assert get_risk_category(score) == category


def test_weights_sum_to_one():
    assert sum(thresholds.FEATURE_WEIGHTS.values()) == pytest.approx(1.0)


# --- Methodology is generated from the same tables -----------------------------

def _sample_values(feature: thresholds.BandedFeature):
    """One value strictly inside every band, derived from the rules."""
    points = sorted({rule.threshold for rule in feature.rules})
    eps = 1e-6
    candidates = [points[0] - eps, points[-1] + 1]
    for value in points:
        candidates += [value - eps, value, value + eps]
    return candidates


@pytest.mark.parametrize("key", list(thresholds.BANDED_FEATURES))
def test_published_bands_describe_engine_behavior(key):
    """For any input, the band whose label describes it carries the engine's risk."""
    feature = thresholds.BANDED_FEATURES[key]
    bands = feature.bands()
    symbol_ops = {">": float.__gt__, "≥": float.__ge__, "<": float.__lt__, "≤": float.__le__}

    def label_matches(label: str, value: float) -> bool:
        conditions = re.findall(r"([<>≤≥]) ([0-9.]+)", label)
        assert conditions, label
        return all(symbol_ops[op](float(value), float(bound)) for op, bound in conditions)

    for value in _sample_values(feature):
        matching = [risk for label, risk in bands if label_matches(label, value)]
        assert matching == [feature.risk_for(value)], (key, value, bands)


def test_scoring_endpoint_matches_tables(anon_client):
    data = anon_client.get("/api/config/scoring").json()
    assert data == thresholds.scoring_config()

    for key, weight in thresholds.FEATURE_WEIGHTS.items():
        assert data["features"][key]["weight"] == weight
    for key, feature in thresholds.BANDED_FEATURES.items():
        assert data["features"][key]["thresholds"] == dict(feature.bands())
    assert data["reason_codes"] == thresholds.REASON_CODES
    assert set(data["categories"]) == {c.name for c in thresholds.CATEGORIES}


def test_category_ranges_and_actions_match_engine():
    for category in thresholds.CATEGORIES:
        assert get_recommended_action(category.name) == category.action
    ranges = thresholds.category_ranges()
    assert ranges["LOW"]["range"] == "0 to < 30"
    assert ranges["CRITICAL"]["range"] == "80 to 100"


def test_reason_code_triggers_match_engine():
    """Each published trigger is exactly where get_reason_codes starts firing."""
    triggers = thresholds.scoring_config()["reason_code_triggers"]
    assert triggers["R01"].startswith("Account Age < 90 days")
    assert triggers["R02"].startswith("Follower/Following Ratio < 0.5")
    assert triggers["R03"].startswith("Posting Frequency > 10 posts/day")
    assert triggers["R04"].startswith("Profile Completeness ≤ 60%")
    assert triggers["R05"].startswith("Engagement < 5%")

    def codes(**kwargs):
        base = dict(username="u", age_days=1000, followers=1000, following=100, posts_per_day=1,
                    profile_completeness=100, avg_likes=500, avg_comments=0)
        base.update(kwargs)
        return {r["code"] for r in analyze_account(**base)["reason_codes"]}

    assert codes() == set()
    assert "R01" in codes(age_days=89) and "R01" not in codes(age_days=90)
    assert "R02" in codes(followers=499, following=1000, avg_likes=50000) and \
        "R02" not in codes(followers=500, following=1000, avg_likes=50000)
    assert "R03" in codes(posts_per_day=10.01) and "R03" not in codes(posts_per_day=10)
    assert "R04" in codes(profile_completeness=60) and "R04" not in codes(profile_completeness=60.01)
    assert "R05" in codes(avg_likes=49.9) and "R05" not in codes(avg_likes=50)


# --- Drift: editing a table changes engine and methodology together ------------

def test_changing_a_threshold_updates_engine_and_methodology(monkeypatch, anon_client):
    changed = dataclasses.replace(
        thresholds.ACCOUNT_AGE,
        rules=(thresholds.Rule(">", 730, 0.0),) + thresholds.ACCOUNT_AGE.rules[1:],
    )
    monkeypatch.setattr(thresholds, "ACCOUNT_AGE", changed)
    monkeypatch.setitem(thresholds.BANDED_FEATURES, "account_age", changed)
    # feature_rules imported the object at module load; point it at the new one.
    from app.scoring import feature_rules
    monkeypatch.setattr(feature_rules, "ACCOUNT_AGE", changed)

    assert calculate_account_age_risk(500) == 10.0  # was 0 with the 365-day rule
    published = anon_client.get("/api/config/scoring").json()["features"]["account_age"]["thresholds"]
    assert published["> 730 days"] == 0.0
    assert published["≥ 180 and ≤ 730 days"] == 10.0


def test_changing_a_reason_rule_updates_engine_and_methodology(monkeypatch, anon_client):
    rules = tuple(
        dataclasses.replace(rule, min_feature_risk=70.0) if rule.code == "R01" else rule
        for rule in thresholds.REASON_CODE_RULES
    )
    monkeypatch.setattr(thresholds, "REASON_CODE_RULES", rules)
    from app.scoring import reason_codes
    monkeypatch.setattr(reason_codes, "REASON_CODE_RULES", rules)

    age_50 = {"account_age": {"available": True, "risk_score": 45.0, "weighted_contribution": 9.0}}
    assert get_reason_codes(age_50) == []
    trigger = anon_client.get("/api/config/scoring").json()["reason_code_triggers"]["R01"]
    assert trigger.startswith("Account Age < 30 days")


def test_feature_rules_have_no_hardcoded_thresholds():
    """Guard against re-introducing literal thresholds in the engine modules."""
    import inspect
    from app.scoring import feature_rules, risk_engine
    for module in (feature_rules, risk_engine):
        source = inspect.getsource(module)
        assert not re.search(r"(>=?|<=?)\s*(365|180|0\.05|0\.2|50|30|60|80)\b", source), module.__name__


# --- Table validation ----------------------------------------------------------

def test_validation_rejects_bad_weights(monkeypatch):
    monkeypatch.setitem(thresholds.FEATURE_WEIGHTS, "engagement", 0.5)
    with pytest.raises(ValueError, match="sum to 1.0"):
        thresholds.validate_tables()


def test_validation_rejects_non_monotonic_bands(monkeypatch):
    broken = dataclasses.replace(thresholds.ENGAGEMENT, default_risk=10.0)
    monkeypatch.setitem(thresholds.BANDED_FEATURES, "engagement", broken)
    with pytest.raises(ValueError, match="non-decreasing"):
        thresholds.validate_tables()


def test_validation_rejects_unknown_reason_feature(monkeypatch):
    rules = thresholds.REASON_CODE_RULES + (thresholds.ReasonCodeRule("R99", "x", "nope", 1.0),)
    monkeypatch.setattr(thresholds, "REASON_CODE_RULES", rules)
    with pytest.raises(ValueError, match="unknown feature"):
        thresholds.validate_tables()


# --- Documentation is generated from the same tables ----------------------------

def test_methodology_doc_tables_are_up_to_date():
    """docs/scoring-methodology.md tables must match thresholds.py (regenerate with
    `python scripts/render_methodology.py` from backend/)."""
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parent.parent / "scripts" / "render_methodology.py"
    spec = importlib.util.spec_from_file_location("render_methodology", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    current = module.DOC.read_bytes().decode("utf-8")
    assert module.render(current) == current, "run: python scripts/render_methodology.py"


def test_methodology_doc_detects_drift(monkeypatch):
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parent.parent / "scripts" / "render_methodology.py"
    spec = importlib.util.spec_from_file_location("render_methodology", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    current = module.DOC.read_bytes().decode("utf-8")
    changed = dataclasses.replace(thresholds.POSTING_FREQUENCY, default_risk=95.0)
    monkeypatch.setitem(thresholds.BANDED_FEATURES, "posting_frequency", changed)
    assert module.render(current) != current
