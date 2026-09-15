import {
  Account,
  AnalysisResponse,
  AccountFormData,
  DashboardSummary,
  RiskDistribution,
  TopRiskAccount,
  PaginatedResponse,
  ImportResult,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Health check
  health: async () => {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse(response);
  },

  // Analysis
  analyzeAccount: async (data: AccountFormData): Promise<AnalysisResponse> => {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  analyzeExistingAccount: async (accountId: number): Promise<AnalysisResponse> => {
    const response = await fetch(`${API_BASE}/accounts/${accountId}/analyze`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  getAccountAnalyses: async (accountId: number) => {
    const response = await fetch(`${API_BASE}/accounts/${accountId}/analysis`);
    return handleResponse(response);
  },

  // Accounts
  getAccounts: async (params: {
    skip?: number;
    limit?: number;
    search?: string;
    category?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<PaginatedResponse<Account>> => {
    const searchParams = new URLSearchParams();
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    if (params.search) searchParams.append('search', params.search);
    if (params.category) searchParams.append('category', params.category);
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params.sort_order) searchParams.append('sort_order', params.sort_order);

    const response = await fetch(`${API_BASE}/accounts?${searchParams}`);
    return handleResponse(response);
  },

  getAccount: async (accountId: number): Promise<Account> => {
    const response = await fetch(`${API_BASE}/accounts/${accountId}`);
    return handleResponse(response);
  },

  createAccount: async (data: AccountFormData): Promise<Account> => {
    const response = await fetch(`${API_BASE}/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const response = await fetch(`${API_BASE}/dashboard/summary`);
    return handleResponse(response);
  },

  getRiskDistribution: async (): Promise<{ distribution: RiskDistribution[] }> => {
    const response = await fetch(`${API_BASE}/dashboard/distribution`);
    return handleResponse(response);
  },

  getTopRiskAccounts: async (limit = 10): Promise<{ accounts: TopRiskAccount[] }> => {
    const response = await fetch(`${API_BASE}/dashboard/top-risk?limit=${limit}`);
    return handleResponse(response);
  },

  // Import
  importCSV: async (file: File): Promise<ImportResult> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/import/csv`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response);
  },

  // Configuration
  getScoringConfig: async () => {
    const response = await fetch(`${API_BASE}/config/scoring`);
    return handleResponse(response);
  },
};