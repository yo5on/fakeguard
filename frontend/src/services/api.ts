import {
  Account,
  AccountFormData,
  AccountQueryParams,
  AnalysisHistoryResponse,
  AnalysisResponse,
  DashboardSummary,
  HealthResponse,
  ImportResult,
  PaginatedResponse,
  RiskDistribution,
  ScoringConfig,
  TopRiskAccount,
} from '../types';

/**
 * Build the API base URL. VITE_API_URL is the backend origin (without /api);
 * trailing slashes are tolerated. Without it, requests go to the same origin
 * (proxied to the backend by Vite in development).
 */
export function resolveApiBase(apiUrl: string | undefined): string {
  const origin = (apiUrl ?? '').trim().replace(/\/+$/, '');
  if (!origin) return '/api';
  return origin.endsWith('/api') ? origin : `${origin}/api`;
}

const API_BASE = resolveApiBase(import.meta.env.VITE_API_URL);

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const LOCATION_PREFIXES = new Set(['body', 'query', 'path']);

interface ValidationIssue {
  loc?: (string | number)[];
  msg?: string;
}

/** Turn a FastAPI error body (string or validation-issue list) into readable text. */
export function formatErrorDetail(detail: unknown, status: number): string {
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((issue: ValidationIssue) => {
        const field = (issue.loc ?? []).filter((part) => !LOCATION_PREFIXES.has(String(part))).join('.');
        return field ? `${field}: ${issue.msg ?? 'invalid value'}` : issue.msg ?? 'Invalid value';
      })
      .join('; ');
  }
  return `Request failed (HTTP ${status})`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch (err) {
    if (init?.signal?.aborted) throw err;
    throw new ApiError('Unable to reach the FakeGuard API. Check that the backend is running.', 0);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(formatErrorDetail(body?.detail, response.status), response.status);
  }
  return response.json() as Promise<T>;
}

function postJson<T>(path: string, data: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export const api = {
  // Health check
  health: () => request<HealthResponse>('/health'),

  // Analysis
  analyzeAccount: (data: AccountFormData) => postJson<AnalysisResponse>('/analyze', data),

  analyzeExistingAccount: (accountId: number) =>
    request<AnalysisResponse>(`/accounts/${accountId}/analyze`, { method: 'POST' }),

  getAccountAnalyses: (accountId: number) =>
    request<AnalysisHistoryResponse>(`/accounts/${accountId}/analysis`),

  // Accounts
  getAccounts: (params: AccountQueryParams, init?: RequestInit) => {
    const searchParams = new URLSearchParams();
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    if (params.search) searchParams.append('search', params.search);
    if (params.category) searchParams.append('category', params.category);
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params.sort_order) searchParams.append('sort_order', params.sort_order);
    return request<PaginatedResponse<Account>>(`/accounts?${searchParams}`, init);
  },

  getAccount: (accountId: number) => request<Account>(`/accounts/${accountId}`),

  createAccount: (data: AccountFormData) => postJson<Account>('/accounts', data),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>('/dashboard/summary'),

  getRiskDistribution: () =>
    request<{ distribution: RiskDistribution[] }>('/dashboard/distribution'),

  getTopRiskAccounts: (limit = 10) =>
    request<{ accounts: TopRiskAccount[] }>(`/dashboard/top-risk?limit=${limit}`),

  // Import
  importCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<ImportResult>('/import/csv', { method: 'POST', body: formData });
  },

  // Configuration
  getScoringConfig: () => request<ScoringConfig>('/config/scoring'),
};
