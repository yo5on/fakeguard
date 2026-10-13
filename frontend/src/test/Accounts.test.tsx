import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Accounts from '../pages/Accounts';
import { api } from '../services/api';
import { Account } from '../types';

const account: Account = {
  id: 1,
  username: 'user_bot_1',
  age_days: 3,
  followers: 5,
  following: 3000,
  posts_per_day: 70,
  profile_completeness: 20,
  avg_likes: 0,
  avg_comments: 0,
  archetype: 'BOT_LIKE',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  latest_analysis: { risk_score: 88.4, category: 'CRITICAL', created_at: '2026-01-01T00:00:00Z' },
};

const page = { accounts: [account], total: 1, skip: 0, limit: 20 };

describe('Accounts', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders accounts and sorts by risk score via an accessible header button', async () => {
    const spy = vi.spyOn(api, 'getAccounts').mockResolvedValue(page);
    render(<Accounts />, { wrapper: MemoryRouter });

    expect(await screen.findByText('user_bot_1')).toBeInTheDocument();
    expect(screen.getByText('88')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: /risk score/i }));

    await waitFor(() =>
      expect(spy).toHaveBeenLastCalledWith(
        expect.objectContaining({ sort_by: 'risk_score', sort_order: 'desc' }),
        expect.anything(),
      ),
    );
    expect(screen.getByRole('columnheader', { name: /risk score/i })).toHaveAttribute(
      'aria-sort',
      'descending',
    );
  });

  it('debounces search input into a single request', async () => {
    const spy = vi.spyOn(api, 'getAccounts').mockResolvedValue(page);
    render(<Accounts />, { wrapper: MemoryRouter });
    await screen.findByText('user_bot_1');
    spy.mockClear();

    const user = userEvent.setup();
    await user.type(screen.getByRole('searchbox', { name: /search accounts/i }), 'bot');

    await waitFor(() =>
      expect(spy).toHaveBeenCalledWith(expect.objectContaining({ search: 'bot' }), expect.anything()),
    );
    const searchTerms = spy.mock.calls.map(([params]) => params.search).filter(Boolean);
    expect(searchTerms).toEqual(['bot']);
  });

  it('lists CSV import row errors', async () => {
    vi.spyOn(api, 'getAccounts').mockResolvedValue(page);
    vi.spyOn(api, 'importCSV').mockResolvedValue({
      imported: 1,
      skipped: 1,
      errors: ['Row 3: age_days: Input should be a valid integer'],
    });
    render(<Accounts />, { wrapper: MemoryRouter });
    await screen.findByText('user_bot_1');

    const user = userEvent.setup();
    const file = new File(['username\n'], 'accounts.csv', { type: 'text/csv' });
    await user.upload(screen.getByLabelText(/choose csv file/i), file);
    await user.click(screen.getByRole('button', { name: 'Import' }));

    expect(await screen.findByText(/Imported: 1, Skipped: 1/)).toBeInTheDocument();
    expect(screen.getByText('Row 3: age_days: Input should be a valid integer')).toBeInTheDocument();
  });
});
