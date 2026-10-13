import { AccountFormData } from '../types';

type NumericField = Exclude<keyof AccountFormData, 'username'>;

/** Form values are kept as strings so that "0" and "" stay distinguishable. */
export type AnalyzerFormValues = Record<keyof AccountFormData, string>;

const INTEGER_FIELDS: ReadonlySet<NumericField> = new Set(['age_days', 'followers', 'following']);

const NUMERIC_FIELDS: NumericField[] = [
  'age_days',
  'followers',
  'following',
  'posts_per_day',
  'profile_completeness',
  'avg_likes',
  'avg_comments',
];

export const initialFormData: AnalyzerFormValues = {
  username: '',
  age_days: '',
  followers: '',
  following: '',
  posts_per_day: '',
  profile_completeness: '',
  avg_likes: '',
  avg_comments: '',
};

/** Convert form strings into the API payload, or return a validation message. */
export function toAccountPayload(values: AnalyzerFormValues): AccountFormData | string {
  const username = values.username.trim();
  if (!username) return 'Username is required.';

  const payload = { username } as AccountFormData;
  for (const field of NUMERIC_FIELDS) {
    const raw = values[field].trim();
    const value = Number(raw);
    if (raw === '' || !Number.isFinite(value) || value < 0) {
      return `${field.replace(/_/g, ' ')} must be a non-negative number.`;
    }
    if (INTEGER_FIELDS.has(field) && !Number.isInteger(value)) {
      return `${field.replace(/_/g, ' ')} must be a whole number.`;
    }
    if (field === 'profile_completeness' && value > 100) {
      return 'profile completeness must be between 0 and 100.';
    }
    payload[field] = value;
  }
  return payload;
}
