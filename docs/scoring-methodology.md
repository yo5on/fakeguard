"# FakeGuard Scoring Methodology

## Overview

FakeGuard uses a transparent, rule-based scoring system to assess potential risk indicators in social media account profiles. The system provides explainable risk scores to help human reviewers prioritize their work.

**Important:** This is a prototype system. Scoring weights and thresholds are heuristics intended for demonstration and are not official standards.

## Scoring Features

The system evaluates five key features, each weighted based on its importance:

| Feature | Weight | Description |
|---------|--------|-------------|
| Account Age | 20% | How long the account has existed |
| Follower/Following Ratio | 25% | Balance between followers and following |
| Posting Frequency | 20% | Average posts per day |
| Profile Completeness | 15% | How complete the profile information is |
| Engagement | 20% | User interaction rates |

**Total Weight:** 100%

## Feature Details

### 1. Account Age (20%)

**Input:** `age_days` (integer)

**Risk Calculation:**

| Age Range | Risk Score |
|-----------|------------|
| > 365 days | 0 (lowest risk) |
| 180-365 days | 10 |
| 90-179 days | 25 |
| 30-89 days | 45 |
| 7-29 days | 70 |
| 0-6 days | 90 (highest risk) |

**Rationale:** Newly created accounts are more likely to be created for malicious purposes or spam. Older accounts have established history.

### 2. Follower/Following Ratio (25%)

**Input:** `followers` (integer), `following` (integer)

**Calculation:** `ratio = followers / following`

**Risk Calculation:**

| Ratio Range | Risk Score |
|-------------|------------|
| ≥ 1.0 | 0 (lowest risk) |
| 0.5 - 0.99 | 20 |
| 0.2 - 0.49 | 40 |
| 0.05 - 0.19 | 70 |
| < 0.05 | 90 (highest risk) |

**Special Case:** If `following = 0`, this feature is marked **unavailable** (cannot divide by zero). The feature is excluded and remaining weights are renormalized.

**Rationale:** Accounts that follow many users but have few followers may be engaged in follow-for-follow schemes or automated following. Legitimate accounts typically have balanced ratios.

### 3. Posting Frequency (20%)

**Input:** `posts_per_day` (float)

**Risk Calculation:**

| Posts/Day | Risk Score |
|-----------|------------|
| ≤ 5 | 0 (lowest risk) |
| 6-10 | 20 |
| 11-20 | 40 |
| 21-50 | 70 |
| > 50 | 90 (highest risk) |

**Rationale:** Extremely high posting frequencies may indicate automated bot behavior. Normal users typically post within moderate ranges.

### 4. Profile Completeness (15%)

**Input:** `profile_completeness` (float, 0-100)

**Calculation:** `profile_risk = 100 - profile_completeness`

**Risk Calculation:**

| Completeness | Risk Score |
|--------------|------------|
| 100% | 0 (lowest risk) |
| 80% | 20 |
| 60% | 40 |
| 40% | 60 |
| 20% | 80 |
| 0% | 100 (highest risk) |

**Validation:** Input must be between 0-100. Values outside this range are rejected.

**Rationale:** Incomplete profiles may indicate throwaway accounts or accounts created quickly for malicious purposes.

### 5. Engagement (20%)

**Input:** `avg_likes` (float), `avg_comments` (float), `followers` (integer)

**Calculation:** `engagement_rate = ((avg_likes + avg_comments) / followers) × 100`

**Risk Calculation:**

| Engagement Rate | Risk Score |
|-----------------|------------|
| ≥ 10% | 0 (lowest risk) |
| 5-9.9% | 20 |
| 2-4.9% | 40 |
| 0.5-1.9% | 70 |
| < 0.5% | 90 (highest risk) |

**Special Case:** If `followers = 0`, this feature is marked **unavailable** (cannot divide by zero). The feature is excluded and remaining weights are renormalized.

**Rationale:** Low engagement despite posting activity may indicate bot accounts or accounts with fake followers. Real users generate organic interactions.

## Final Score Calculation

### Standard Calculation

For each **available** feature:

```
weighted_contribution = feature_risk × feature_weight
```

Final score:

```
final_score = sum(weighted_contributions) / sum(available_weights)
```

### Example

**Account Data:**
- Age: 50 days
- Followers: 100
- Following: 1000
- Posts/day: 30
- Profile: 40%
- Avg likes: 2
- Avg comments: 0.5

**Feature Calculations:**

1. **Account Age:** 50 days → Risk 45, Weight 0.20 → Contribution 9.0
2. **Follower Ratio:** 100/1000 = 0.1 → Risk 70, Weight 0.25 → Contribution 17.5
3. **Posting Frequency:** 30 posts/day → Risk 70, Weight 0.20 → Contribution 14.0
4. **Profile Completeness:** 100 - 40 = 60 → Risk 60, Weight 0.15 → Contribution 9.0
5. **Engagement:** (2 + 0.5)/100 × 100 = 2.5% → Risk 40, Weight 0.20 → Contribution 8.0

**Final Score:**
```
(9.0 + 17.5 + 14.0 + 9.0 + 8.0) / 1.0 = 57.5
```

**Result:** 57.5 / 100 → **MEDIUM RISK** → "Monitor account"

## Risk Categories

Risk categories are determined using the **precise** internal score (not rounded):

| Category | Score Range | Recommended Action |
|----------|-------------|-------------------|
| LOW | 0 - 29.9 | No immediate action |
| MEDIUM | 30 - 59.9 | Monitor account |
| HIGH | 60 - 79.9 | Manual review recommended |
| CRITICAL | 80 - 100 | Priority investigation |

**Important:** Category is determined BEFORE rounding for display. A score of 29.95 is LOW, not MEDIUM.

## Missing Data Handling

### Problem

Some features cannot be calculated when certain data is missing:
- **Follower ratio** requires `following > 0`
- **Engagement** requires `followers > 0`

### Solution: Renormalization

When a feature is unavailable:

1. Mark feature as `available: false`
2. Set `weighted_contribution = 0`
3. Exclude feature weight from denominator
4. Recalculate score using only available features

### Example with Missing Data

**Account Data:**
- Age: 100 days
- Followers: 0
- Following: 0
- Posts/day: 5
- Profile: 80%
- Avg likes: 0
- Avg comments: 0

**Available Features:**
- Account Age: 25 (weight 0.20)
- Posting Frequency: 0 (weight 0.20)
- Profile Completeness: 20 (weight 0.15)

**Unavailable:**
- Follower Ratio (weight 0.25)
- Engagement (weight 0.20)

**Calculation:**
```
Available weights: 0.20 + 0.20 + 0.15 = 0.55
Weighted sum: (25 × 0.20) + (0 × 0.20) + (20 × 0.15) = 8.0
Final score: 8.0 / 0.55 = 14.5
```

**Result:** 14.5 / 100 → **LOW RISK**

**Key Point:** The system does NOT assume maximum risk for missing features. It evaluates based on available information.

## Reason Codes

The system generates human-readable reason codes when specific risk indicators are detected:

| Code | Description | Trigger |
|------|-------------|---------|
| R01 | Very new account | Age < 30 days (risk ≥ 45) |
| R02 | Extremely low follower/following ratio | Ratio < 0.2 (risk ≥ 40) |
| R03 | High posting frequency | Posts/day > 20 (risk ≥ 40) |
| R04 | Incomplete profile | Completeness < 60% (risk ≥ 40) |
| R05 | Very low engagement | Engagement < 2% (risk ≥ 40) |

Reason codes are sorted by **weighted contribution** (highest first) to show which factors most influence the score.

## Transparency and Explainability

Every analysis result includes:

1. **Final risk score** (0-100)
2. **Risk category** (LOW/MEDIUM/HIGH/CRITICAL)
3. **Recommended action**
4. **Feature-by-feature breakdown:**
   - Individual risk score
   - Weighted contribution
   - Availability status
   - Raw values
5. **Reason codes** explaining specific concerns
6. **Total weight used** (shows renormalization)

This transparency allows reviewers to:
- Understand why an account received its score
- Validate the logic
- Make informed decisions
- Contest or adjust assessments

## Limitations

### What This System Does NOT Do

- **Does not definitively classify accounts as fake**
- **Does not use machine learning** (rule-based only)
- **Does not access real social media data**
- **Does not consider temporal patterns** (e.g., posting times)
- **Does not analyze content** (text, images, links)
- **Does not examine network connections**
- **Does not verify identity**

### Prototype Assumptions

- Feature weights are heuristic estimates
- Thresholds are not validated against real data
- No false positive/negative analysis
- No A/B testing or optimization
- Simplified engagement calculation

## Future Enhancements

### Potential Improvements

1. **Machine Learning Integration:**
   - Isolation Forest for anomaly detection
   - Supervised classification with labeled data
   - Temporal behavioral analysis

2. **Additional Features:**
   - Account verification status
   - Bio completeness and quality
   - Link analysis (spam/phishing detection)
   - Posting time patterns
   - Content sentiment analysis

3. **Adaptive Scoring:**
   - Platform-specific thresholds
   - Domain-specific weights (e.g., news vs. entertainment)
   - Time-based adjustments

4. **Validation:**
   - Benchmark against labeled datasets
   - False positive/negative rate measurement
   - Precision/recall optimization

## Human-in-the-Loop

**Critical Principle:** FakeGuard is a decision-support tool, NOT an autonomous enforcement system.

### Reviewer Workflow

1. System flags high-risk accounts
2. Human reviewer examines flagged accounts
3. Reviewer considers system explanation
4. Reviewer applies domain expertise
5. Reviewer makes final decision
6. Action taken (if any) by authorized personnel

### Why Human Review Matters

- Context matters (cultural, linguistic, domain-specific)
- Edge cases require judgment
- False positives must be avoided
- Legal and ethical implications
- System limitations and biases

## Disclaimer

**The scoring weights and thresholds are prototype heuristics intended for demonstration and evaluation. They are not official government, law-enforcement, or social-media-platform standards.**

This system is designed for:
- Educational purposes
- Prototype demonstration
- Research and development
- Proof of concept

It should NOT be used for:
- Production account moderation without validation
- Automated enforcement actions
- Legal proceedings without expert review
- High-stakes decisions without human oversight"