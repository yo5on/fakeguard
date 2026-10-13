import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Analyzer from '../pages/Analyzer';
import { api } from '../services/api';
import { AnalysisResponse } from '../types';

const response: AnalysisResponse = {
  account: {
    id: 0,
    username: 'zero_followers',
    age_days: 10,
    followers: 0,
    following: 0,
    posts_per_day: 1,
    profile_completeness: 50,
    avg_likes: 0,
    avg_comments: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  analysis: {
    risk_score: 46,
    category: 'MEDIUM',
    recommended_action: 'Monitor account',
    features: [
      { feature: 'Account Age', risk_score: 70, weighted_contribution: 14, available: true, details: '10 days old' },
      {
        feature: 'Engagement',
        risk_score: 0,
        weighted_contribution: 0,
        available: false,
        details: 'Cannot calculate (followers = 0)',
      },
    ],
    reason_codes: [],
    total_weight_used: 0.55,
  },
  timestamp: '2026-01-01T00:00:00Z',
};

const FIELDS: [RegExp, string][] = [
  [/^username/i, 'zero_followers'],
  [/account age/i, '10'],
  [/^followers/i, '0'],
  [/^following/i, '0'],
  [/posts per day/i, '1'],
  [/profile completeness/i, '50'],
  [/avg likes/i, '0'],
  [/avg comments/i, '0'],
];

async function fillForm() {
  const user = userEvent.setup();
  for (const [label, value] of FIELDS) {
    await user.type(screen.getByLabelText(label), value);
  }
  return user;
}

describe('Analyzer', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('submits zero values instead of blocking the form', async () => {
    const spy = vi.spyOn(api, 'analyzeAccount').mockResolvedValue(response);
    render(<Analyzer />, { wrapper: MemoryRouter });

    const user = await fillForm();

    // The zero stays visible in the field (it used to be rendered as empty).
    expect(screen.getByLabelText(/^followers/i)).toHaveValue(0);

    await user.click(screen.getByRole('button', { name: /analyze account/i }));

    expect(spy).toHaveBeenCalledWith(expect.objectContaining({ followers: 0, following: 0 }));
    expect(await screen.findByText('Analysis Results')).toBeInTheDocument();
    expect(screen.getByText('Monitor account')).toBeInTheDocument();
    expect(screen.getByText('Cannot calculate (followers = 0)')).toBeInTheDocument();
  });

  it('shows API errors as an alert', async () => {
    vi.spyOn(api, 'analyzeAccount').mockRejectedValue(new Error('username: bad value'));
    render(<Analyzer />, { wrapper: MemoryRouter });

    const user = await fillForm();
    await user.click(screen.getByRole('button', { name: /analyze account/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('username: bad value');
  });
});
