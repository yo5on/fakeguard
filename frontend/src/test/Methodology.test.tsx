import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RiskBreakdown from '../components/RiskBreakdown';
import ScoringMethodology from '../pages/ScoringMethodology';
import { api } from '../services/api';
import { ScoringConfig } from '../types';

const config: ScoringConfig = {
  features: {
    account_age: { label: 'Account Age', weight: 0.2, thresholds: { '> 365 days': 0, '< 7 days': 90 } },
    follower_ratio: {
      label: 'Follower/Following Ratio',
      weight: 0.25,
      thresholds: { '≥ 1': 0 },
      definition: 'followers / following',
      unavailable_when: 'following = 0',
    },
    profile_completeness: { label: 'Profile Completeness', weight: 0.15, formula: 'risk = 100 - completeness' },
  },
  categories: { LOW: { range: '0 to < 30', action: 'No immediate action' } },
  reason_codes: { R01: 'Very new account' },
  reason_code_triggers: { R01: 'Account Age < 90 days (feature risk ≥ 45)' },
  disclaimer: 'Prototype heuristics.',
};

describe('ScoringMethodology', () => {
  afterEach(() => vi.restoreAllMocks());

  it('renders served thresholds, triggers and the accurate missing-data rule', async () => {
    vi.spyOn(api, 'getScoringConfig').mockResolvedValue(config);
    render(<ScoringMethodology />, { wrapper: MemoryRouter });

    expect(await screen.findByText('Follower/Following Ratio')).toBeInTheDocument();
    expect(screen.getByText('> 365 days')).toBeInTheDocument();
    expect(screen.getByText(/Trigger: Account Age < 90 days/)).toBeInTheDocument();
    const page = document.body.textContent ?? '';
    expect(page).toContain('Unavailable when: following = 0');
    expect(page).toContain('Measured as: followers / following');
    expect(page).toContain('weighted average of the features that could be measured');
    expect(page).toContain('21.5 ÷ 0.55 ≈ 39');
    // Regression: the old wording claimed features "scale to represent 100%".
    expect(page).not.toMatch(/scaled? to represent 100%/i);
  });
});

describe('RiskBreakdown', () => {
  const features = [
    { feature: 'Account Age', risk_score: 70, weighted_contribution: 14, available: true },
    { feature: 'Posting Frequency', risk_score: 0, weighted_contribution: 0, available: true },
    { feature: 'Profile Completeness', risk_score: 50, weighted_contribution: 7.5, available: true },
    { feature: 'Engagement', risk_score: 0, weighted_contribution: 0, available: false },
  ];

  it('explains the division when features are missing', () => {
    render(<RiskBreakdown features={features} totalWeightUsed={0.55} />);
    expect(screen.getByText(/only 55% of the weight is available/)).toHaveTextContent('21.50 ÷ 0.55 = 39.1');
  });

  it('shows no note when every feature is available', () => {
    render(<RiskBreakdown features={features.slice(0, 3)} totalWeightUsed={1} />);
    expect(screen.queryByText(/of the weight is available/)).not.toBeInTheDocument();
  });
});
