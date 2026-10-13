import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, api, formatErrorDetail, resolveApiBase } from '../services/api';

describe('resolveApiBase', () => {
  it('falls back to same-origin /api', () => {
    expect(resolveApiBase(undefined)).toBe('/api');
    expect(resolveApiBase('  ')).toBe('/api');
  });

  it('appends /api to the backend origin', () => {
    expect(resolveApiBase('https://api.example.com')).toBe('https://api.example.com/api');
  });

  it('tolerates trailing slashes and an existing /api suffix', () => {
    expect(resolveApiBase('https://api.example.com/')).toBe('https://api.example.com/api');
    expect(resolveApiBase('https://api.example.com/api/')).toBe('https://api.example.com/api');
  });
});

describe('formatErrorDetail', () => {
  it('passes string details through', () => {
    expect(formatErrorDetail('Account not found', 404)).toBe('Account not found');
  });

  it('formats FastAPI validation errors instead of "[object Object]"', () => {
    const detail = [
      { loc: ['body', 'age_days'], msg: 'Input should be greater than or equal to 0' },
      { loc: ['query', 'limit'], msg: 'Input should be less than or equal to 100' },
    ];
    expect(formatErrorDetail(detail, 422)).toBe(
      'age_days: Input should be greater than or equal to 0; limit: Input should be less than or equal to 100',
    );
  });

  it('falls back to the status code', () => {
    expect(formatErrorDetail(undefined, 500)).toBe('Request failed (HTTP 500)');
  });
});

describe('api request handling', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('throws ApiError with a readable message for error responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: [{ loc: ['path', 'account_id'], msg: 'bad id' }] }), {
          status: 422,
        }),
      ),
    );

    const error = await api.getAccount(1).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(422);
    expect((error as ApiError).message).toBe('account_id: bad id');
  });

  it('reports network failures clearly', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(api.health()).rejects.toThrow(/Unable to reach the FakeGuard API/);
  });

  it('builds the accounts query string', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ accounts: [], total: 0, skip: 0, limit: 20 })),
    );
    vi.stubGlobal('fetch', fetchMock);

    await api.getAccounts({ skip: 20, limit: 20, search: 'bot_1', sort_by: 'risk_score', sort_order: 'desc' });
    expect(fetchMock.mock.calls[0][0]).toBe(
      '/api/accounts?skip=20&limit=20&search=bot_1&sort_by=risk_score&sort_order=desc',
    );
  });
});
