import { describe, expect, it } from 'vitest';
import { initialFormData, toAccountPayload } from '../utils/accountForm';

const filled = {
  username: ' edge_case ',
  age_days: '30',
  followers: '0',
  following: '0',
  posts_per_day: '0',
  profile_completeness: '0',
  avg_likes: '0',
  avg_comments: '0',
};

describe('toAccountPayload', () => {
  it('accepts zero values (regression: 0 used to be treated as empty)', () => {
    expect(toAccountPayload(filled)).toEqual({
      username: 'edge_case',
      age_days: 30,
      followers: 0,
      following: 0,
      posts_per_day: 0,
      profile_completeness: 0,
      avg_likes: 0,
      avg_comments: 0,
    });
  });

  it('requires every field', () => {
    expect(toAccountPayload(initialFormData)).toBe('Username is required.');
    expect(toAccountPayload({ ...filled, followers: '' })).toMatch(/followers/);
  });

  it('rejects negative, fractional-integer and out-of-range values', () => {
    expect(toAccountPayload({ ...filled, avg_likes: '-1' })).toMatch(/avg likes/);
    expect(toAccountPayload({ ...filled, age_days: '1.5' })).toMatch(/whole number/);
    expect(toAccountPayload({ ...filled, profile_completeness: '101' })).toMatch(/between 0 and 100/);
  });

  it('allows decimals for rate fields', () => {
    expect(toAccountPayload({ ...filled, posts_per_day: '3.55' })).toMatchObject({ posts_per_day: 3.55 });
  });
});
