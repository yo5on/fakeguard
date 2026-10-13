import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Header from '../components/Header';

describe('Header', () => {
  it('marks the Accounts link active on nested account routes', () => {
    render(
      <MemoryRouter initialEntries={['/accounts/42']}>
        <Header />
      </MemoryRouter>,
    );

    const accounts = screen.getByRole('link', { name: 'Accounts' });
    expect(accounts).toHaveClass('active');
    expect(accounts).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'Dashboard' })).not.toHaveClass('active');
  });
});
