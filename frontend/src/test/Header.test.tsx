import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Header from '../components/Header';
import { WithAuth, authState } from './authTestUtils';

function renderHeader(path: string, auth = authState()) {
  render(
    <WithAuth value={auth}>
      <MemoryRouter initialEntries={[path]}>
        <Header />
      </MemoryRouter>
    </WithAuth>,
  );
  return auth;
}

describe('Header', () => {
  it('marks the Accounts link active on nested account routes', () => {
    renderHeader('/accounts/42');

    const accounts = screen.getByRole('link', { name: 'Accounts' });
    expect(accounts).toHaveClass('active');
    expect(accounts).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'Dashboard' })).not.toHaveClass('active');
  });

  it('shows the signed-in user and signs out', async () => {
    const auth = renderHeader('/dashboard');
    expect(screen.getByText('reviewer')).toBeInTheDocument();

    await userEvent.setup().click(screen.getByRole('button', { name: 'Sign out' }));
    expect(auth.logout).toHaveBeenCalled();
  });

  it('hides the session controls when signed out or when auth is disabled', () => {
    renderHeader('/login', authState({ username: null }));
    expect(screen.queryByRole('button', { name: 'Sign out' })).not.toBeInTheDocument();
  });

  it('hides the session controls when the server disables auth', () => {
    renderHeader('/dashboard', authState({ authRequired: false, username: 'anonymous' }));
    expect(screen.queryByRole('button', { name: 'Sign out' })).not.toBeInTheDocument();
  });
});
