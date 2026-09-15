export interface Account {
  id: number;
  username: string;
  age_days: number;
  followers: number;
  following: number;
  posts_per_day: number;
  profile_completeness: number;
  avg_likes: number;
  avg_comments: number;
  archetype?: string;
  created_at: string;
  updated_at: string;
  latest_analysis?: LatestAnalysis;
}

export interface LatestAnalysis {
  id?: number;
  risk_score: number;
  category: string;
  recommended_action?: string;
  details?: AnalysisResult;
  created_at: string;
}

export interface FeatureAnalysis {
  feature: string;
  risk_score: number;
  weighted_contribution: number;
  available: boolean;
  details?: string;
}

export interface ReasonCode {
  code: string;
  description: string;
  feature: string;
  feature_score: number;
  weighted_contribution: number;
}

export interface AnalysisResult {
  risk_score: number;
  category: string;
  recommended_action: string;
  features: FeatureAnalysis[];
  reason_codes: ReasonCode[];
  total_weight_used: number;
}

export interface AnalysisResponse {
  account: Account;
  analysis: AnalysisResult;
  timestamp: string;
}

export interface DashboardSummary {
  total_accounts: number;
  low_risk: number;
  medium_risk: number;
  high_risk: number;
  critical_risk: number;
  average_risk_score: number;
}

export interface RiskDistribution {
  category: string;
  count: number;
}

export interface TopRiskAccount {
  id: number;
  username: string;
  risk_score: number;
  category: string;
  last_analyzed: string;
}

export interface AccountFormData {
  username: string;
  age_days: number;
  followers: number;
  following: number;
  posts_per_day: number;
  profile_completeness: number;
  avg_likes: number;
  avg_comments: number;
}

export interface PaginatedResponse<T> {
  accounts: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ImportResult {
  imported: number;
  skipped: number;
  errors: string[];
}