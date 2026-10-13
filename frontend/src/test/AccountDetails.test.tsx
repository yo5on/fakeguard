import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import AccountDetails from '../pages/AccountDetails';
import { api } from '../services/api';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/accounts/:id" element={<AccountDetails />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('AccountDetails', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('rejects a non-numeric id without calling the API', () => {
    const spy = vi.spyOn(api, 'getAccount');
    renderAt('/accounts/abc');
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid account ID');
    expect(spy).not.toHaveBeenCalled();
  });

  it('offers a first analysis for unanalyzed accounts', async () => {
    vi.spyOn(api, 'getAccount').mockResolvedValue({
      id: 7,
      username: 'quiet_user',
      age_days: 400,
      followers: 100,
      following: 90,
      posts_per_day: 1,
      profile_completeness: 90,
      avg_likes: 10,
      avg_comments: 1,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
      latest_analysis: null,
    });
    vi.spyOn(api, 'getAccountAnalyses').mockResolvedValue({
      account_id: 7,
      username: 'quiet_user',
      analyses: [],
    });

    renderAt('/accounts/7');
    expect(await screen.findByRole('heading', { name: 'quiet_user' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Analyze Account' })).toBeInTheDocument();
  });
});
