"""
Single source of truth for the scoring rules.

The risk engine evaluates these tables and the /api/config/scoring
methodology endpoint renders them, so the two cannot drift apart. Changing a
number here changes both the scores and the published methodology.

A banded feature is a list of rules evaluated top to bottom; the first rule
whose comparison holds gives the feature risk, otherwise ``default_risk``
applies. Range labels are generated from the rules, never written by hand.
"""
import operator
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

_COMPARATORS: Dict[str, Tuple[Callable[[float, float], bool], str, str]] = {
    # op: (function, symbol when it holds, symbol when it does not hold)
    ">": (operator.gt, ">", "≤"),
    ">=": (operator.ge, "≥", "<"),
    "<=": (operator.le, "≤", ">"),
    "<": (operator.lt, "<", "≥"),
}


@dataclass(frozen=True)
class Rule:
    op: str
    threshold: float
    risk: float

    def matches(self, value: float) -> bool:
        return _COMPARATORS[self.op][0](value, self.threshold)


@dataclass(frozen=True)
class BandedFeature:
    rules: Tuple[Rule, ...]
    default_risk: float
    unit: str = ""

    def risk_for(self, value: float) -> float:
        for rule in self.rules:
            if rule.matches(value):
                return rule.risk
        return self.default_risk

    def bands(self) -> List[Tuple[str, float]]:
        """(label, risk) for every band, in evaluation order."""
        result = []
        previous: Optional[Rule] = None
        for rule in self.rules:
            parts = [_holds(rule)]
            if previous is not None:
                parts.append(_fails(previous))
            # Lower bound first: "> 5 and ≤ 10", "≥ 90 and < 180".
            parts.sort(key=lambda part: 0 if part[0] in ">≥" else 1)
            result.append((self.label(" and ".join(parts)), rule.risk))
            previous = rule
        result.append((self.label(_fails(self.rules[-1])), self.default_risk))
        return result

    def trigger_condition(self, min_risk: float) -> str:
        """Input condition under which the feature risk is >= ``min_risk``."""
        risks = [rule.risk for rule in self.rules] + [self.default_risk]
        index = next(i for i, risk in enumerate(risks) if risk >= min_risk)
        if index == 0:
            return "any value"
        return self.label(_fails(self.rules[index - 1]))

    def label(self, condition: str) -> str:
        if not self.unit:
            return condition
        separator = "" if self.unit.startswith("%") else " "
        return f"{condition}{separator}{self.unit}"


def _holds(rule: Rule) -> str:
    return f"{_COMPARATORS[rule.op][1]} {_fmt(rule.threshold)}"


def _fails(rule: Rule) -> str:
    return f"{_COMPARATORS[rule.op][2]} {_fmt(rule.threshold)}"


def _fmt(value: float) -> str:
    return f"{value:g}"


# --- Feature weights (must sum to 1.0) --------------------------------------

FEATURE_WEIGHTS: Dict[str, float] = {
    "account_age": 0.20,
    "follower_ratio": 0.25,
    "posting_frequency": 0.20,
    "profile_completeness": 0.15,
    "engagement": 0.20,
}

FEATURE_LABELS: Dict[str, str] = {
    "account_age": "Account Age",
    "follower_ratio": "Follower/Following Ratio",
    "posting_frequency": "Posting Frequency",
    "profile_completeness": "Profile Completeness",
    "engagement": "Engagement",
}

# --- Banded features ----------------------------------------------------------

ACCOUNT_AGE = BandedFeature(
    rules=(
        Rule(">", 365, 0.0),
        Rule(">=", 180, 10.0),
        Rule(">=", 90, 25.0),
        Rule(">=", 30, 45.0),
        Rule(">=", 7, 70.0),
    ),
    default_risk=90.0,
    unit="days",
)

FOLLOWER_RATIO = BandedFeature(
    rules=(
        Rule(">=", 1.0, 0.0),
        Rule(">=", 0.5, 20.0),
        Rule(">=", 0.2, 40.0),
        Rule(">=", 0.05, 70.0),
    ),
    default_risk=90.0,
)

POSTING_FREQUENCY = BandedFeature(
    rules=(
        Rule("<=", 5, 0.0),
        Rule("<=", 10, 20.0),
        Rule("<=", 20, 40.0),
        Rule("<=", 50, 70.0),
    ),
    default_risk=90.0,
    unit="posts/day",
)

ENGAGEMENT = BandedFeature(
    rules=(
        Rule(">=", 10, 0.0),
        Rule(">=", 5, 20.0),
        Rule(">=", 2, 40.0),
        Rule(">=", 0.5, 70.0),
    ),
    default_risk=90.0,
    unit="%",
)

BANDED_FEATURES: Dict[str, BandedFeature] = {
    "account_age": ACCOUNT_AGE,
    "follower_ratio": FOLLOWER_RATIO,
    "posting_frequency": POSTING_FREQUENCY,
    "engagement": ENGAGEMENT,
}

PROFILE_COMPLETENESS_FORMULA = "risk = 100 - completeness"

# When a feature's input makes it impossible to compute.
UNAVAILABLE_CONDITIONS: Dict[str, str] = {
    "follower_ratio": "following = 0",
    "engagement": "followers = 0",
}

FEATURE_DEFINITIONS: Dict[str, str] = {
    "follower_ratio": "followers / following",
    "engagement": "(avg_likes + avg_comments) / followers × 100",
}

# --- Risk categories ----------------------------------------------------------

@dataclass(frozen=True)
class Category:
    name: str
    upper_exclusive: Optional[float]  # None = no upper bound (up to 100)
    action: str


CATEGORIES: Tuple[Category, ...] = (
    Category("LOW", 30.0, "No immediate action"),
    Category("MEDIUM", 60.0, "Monitor account"),
    Category("HIGH", 80.0, "Manual review recommended"),
    Category("CRITICAL", None, "Priority investigation"),
)

CATEGORY_ACTIONS: Dict[str, str] = {c.name: c.action for c in CATEGORIES}


def category_for(score: float) -> str:
    for category in CATEGORIES:
        if category.upper_exclusive is None or score < category.upper_exclusive:
            return category.name
    raise AssertionError("unreachable: last category is unbounded")


def category_ranges() -> Dict[str, Dict[str, str]]:
    result = {}
    lower = 0.0
    for category in CATEGORIES:
        if category.upper_exclusive is None:
            label = f"{_fmt(lower)} to 100"
        else:
            label = f"{_fmt(lower)} to < {_fmt(category.upper_exclusive)}"
            lower = category.upper_exclusive
        result[category.name] = {"range": label, "action": category.action}
    return result


# --- Reason codes -------------------------------------------------------------

@dataclass(frozen=True)
class ReasonCodeRule:
    code: str
    description: str
    feature: str
    min_feature_risk: float


REASON_CODE_RULES: Tuple[ReasonCodeRule, ...] = (
    ReasonCodeRule("R01", "Very new account", "account_age", 45.0),
    ReasonCodeRule("R02", "Extremely low follower/following ratio", "follower_ratio", 40.0),
    ReasonCodeRule("R03", "High posting frequency", "posting_frequency", 40.0),
    ReasonCodeRule("R04", "Incomplete profile", "profile_completeness", 40.0),
    ReasonCodeRule("R05", "Very low engagement", "engagement", 40.0),
)

REASON_CODES: Dict[str, str] = {rule.code: rule.description for rule in REASON_CODE_RULES}


def reason_code_trigger(rule: ReasonCodeRule) -> str:
    """Describe, in input terms, when a reason code fires."""
    label = FEATURE_LABELS[rule.feature]
    if rule.feature == "profile_completeness":
        return f"{label} ≤ {_fmt(100 - rule.min_feature_risk)}% (feature risk ≥ {_fmt(rule.min_feature_risk)})"
    condition = BANDED_FEATURES[rule.feature].trigger_condition(rule.min_feature_risk)
    return f"{label} {condition} (feature risk ≥ {_fmt(rule.min_feature_risk)})"


DISCLAIMER = (
    "The scoring weights and thresholds are prototype heuristics intended for demonstration "
    "and evaluation. They are not official government, law-enforcement, or "
    "social-media-platform standards."
)

MISSING_DATA_RULE = (
    "Features that cannot be calculated are excluded. The final score is the weighted "
    "average of the available features: sum(feature risk × weight) / sum(weights of "
    "available features). Excluded features count neither as zero nor as maximum risk."
)


def scoring_config() -> Dict[str, Any]:
    """Methodology payload for /api/config/scoring, generated from the tables above."""
    features: Dict[str, Dict[str, Any]] = {}
    for key in FEATURE_WEIGHTS:
        entry: Dict[str, Any] = {"label": FEATURE_LABELS[key], "weight": FEATURE_WEIGHTS[key]}
        if key in BANDED_FEATURES:
            entry["thresholds"] = {label: risk for label, risk in BANDED_FEATURES[key].bands()}
        else:
            entry["formula"] = PROFILE_COMPLETENESS_FORMULA
        if key in FEATURE_DEFINITIONS:
            entry["definition"] = FEATURE_DEFINITIONS[key]
        if key in UNAVAILABLE_CONDITIONS:
            entry["unavailable_when"] = UNAVAILABLE_CONDITIONS[key]
        features[key] = entry

    return {
        "features": features,
        "categories": category_ranges(),
        "reason_codes": REASON_CODES,
        "reason_code_triggers": {rule.code: reason_code_trigger(rule) for rule in REASON_CODE_RULES},
        "missing_data": MISSING_DATA_RULE,
        "disclaimer": DISCLAIMER,
    }


def validate_tables(features: Sequence[str] = tuple(FEATURE_WEIGHTS)) -> None:
    """Sanity checks run at import time so a bad edit fails fast."""
    if abs(sum(FEATURE_WEIGHTS.values()) - 1.0) > 1e-9:
        raise ValueError("FEATURE_WEIGHTS must sum to 1.0")
    if set(FEATURE_WEIGHTS) != set(FEATURE_LABELS):
        raise ValueError("FEATURE_WEIGHTS and FEATURE_LABELS must have the same keys")
    for rule in REASON_CODE_RULES:
        if rule.feature not in features:
            raise ValueError(f"Reason code {rule.code} references unknown feature {rule.feature}")
    for key, feature in BANDED_FEATURES.items():
        risks = [r.risk for r in feature.rules] + [feature.default_risk]
        # trigger_condition() relies on risk never decreasing from band to band.
        if risks != sorted(risks):
            raise ValueError(f"{key}: band risks must be non-decreasing in evaluation order")
    bounds = [c.upper_exclusive for c in CATEGORIES]
    if bounds[-1] is not None or bounds[:-1] != sorted(b for b in bounds[:-1] if b is not None):
        raise ValueError("CATEGORIES must be ascending with an unbounded last entry")


validate_tables()
