import pandas as pd
import numpy as np
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

def generate_normal_accounts(n=400):
    """Generate normal legitimate accounts."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(180, 2000)
        followers = np.random.randint(100, 5000)
        following = np.random.randint(50, int(followers * 1.5))
        posts_per_day = np.random.uniform(0.5, 5)
        profile_completeness = np.random.uniform(70, 100)
        avg_likes = followers * np.random.uniform(0.02, 0.10)
        avg_comments = avg_likes * np.random.uniform(0.05, 0.15)
        
        accounts.append({
            'username': f'user_normal_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'NORMAL'
        })
    return accounts

def generate_new_legitimate_accounts(n=150):
    """Generate new but legitimate accounts."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(1, 90)
        followers = np.random.randint(10, 200)
        following = np.random.randint(20, 300)
        posts_per_day = np.random.uniform(0.5, 4)
        profile_completeness = np.random.uniform(60, 95)
        avg_likes = followers * np.random.uniform(0.03, 0.12)
        avg_comments = avg_likes * np.random.uniform(0.05, 0.15)
        
        accounts.append({
            'username': f'user_new_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'NEW_LEGITIMATE'
        })
    return accounts

def generate_suspicious_accounts(n=200):
    """Generate suspicious bot-like accounts."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(1, 180)
        followers = np.random.randint(5, 100)
        following = np.random.randint(500, 5000)
        posts_per_day = np.random.uniform(15, 80)
        profile_completeness = np.random.uniform(20, 60)
        avg_likes = followers * np.random.uniform(0.001, 0.02)
        avg_comments = avg_likes * np.random.uniform(0.01, 0.05)
        
        accounts.append({
            'username': f'user_suspicious_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'SUSPICIOUS'
        })
    return accounts

def generate_influencer_accounts(n=100):
    """Generate influencer accounts."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(365, 3000)
        followers = np.random.randint(10000, 500000)
        following = np.random.randint(100, 2000)
        posts_per_day = np.random.uniform(1, 8)
        profile_completeness = np.random.uniform(85, 100)
        avg_likes = followers * np.random.uniform(0.05, 0.15)
        avg_comments = avg_likes * np.random.uniform(0.08, 0.20)
        
        accounts.append({
            'username': f'influencer_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'INFLUENCER'
        })
    return accounts

def generate_bot_like_accounts(n=80):
    """Generate obvious bot-like accounts."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(1, 30)
        followers = np.random.randint(1, 50)
        following = np.random.randint(1000, 8000)
        posts_per_day = np.random.uniform(30, 150)
        profile_completeness = np.random.uniform(10, 40)
        avg_likes = followers * np.random.uniform(0.0001, 0.005)
        avg_comments = avg_likes * np.random.uniform(0.001, 0.02)
        
        accounts.append({
            'username': f'bot_like_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'BOT_LIKE'
        })
    return accounts

def generate_incomplete_profile_accounts(n=40):
    """Generate accounts with incomplete profiles."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(30, 500)
        followers = np.random.randint(50, 1000)
        following = np.random.randint(30, 800)
        posts_per_day = np.random.uniform(1, 10)
        profile_completeness = np.random.uniform(0, 40)
        avg_likes = followers * np.random.uniform(0.01, 0.08)
        avg_comments = avg_likes * np.random.uniform(0.03, 0.10)
        
        accounts.append({
            'username': f'incomplete_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'INCOMPLETE_PROFILE'
        })
    return accounts

def generate_low_engagement_accounts(n=30):
    """Generate accounts with very low engagement."""
    accounts = []
    for i in range(n):
        age_days = np.random.randint(90, 800)
        followers = np.random.randint(500, 5000)
        following = np.random.randint(100, 1000)
        posts_per_day = np.random.uniform(2, 12)
        profile_completeness = np.random.uniform(50, 85)
        avg_likes = followers * np.random.uniform(0.0001, 0.005)
        avg_comments = avg_likes * np.random.uniform(0.001, 0.03)
        
        accounts.append({
            'username': f'low_engagement_{i+1}',
            'age_days': age_days,
            'followers': followers,
            'following': following,
            'posts_per_day': round(posts_per_day, 2),
            'profile_completeness': round(profile_completeness, 1),
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'archetype': 'LOW_ENGAGEMENT'
        })
    return accounts

def generate_edge_cases():
    """Generate edge case accounts for testing."""
    accounts = []
    
    # Zero followers
    accounts.append({
        'username': 'edge_zero_followers',
        'age_days': 100,
        'followers': 0,
        'following': 500,
        'posts_per_day': 5.0,
        'profile_completeness': 80.0,
        'avg_likes': 0.0,
        'avg_comments': 0.0,
        'archetype': 'EDGE_CASE'
    })
    
    # Zero following
    accounts.append({
        'username': 'edge_zero_following',
        'age_days': 200,
        'followers': 1000,
        'following': 0,
        'posts_per_day': 3.0,
        'profile_completeness': 90.0,
        'avg_likes': 50.0,
        'avg_comments': 5.0,
        'archetype': 'EDGE_CASE'
    })
    
    # Both zero
    accounts.append({
        'username': 'edge_both_zero',
        'age_days': 50,
        'followers': 0,
        'following': 0,
        'posts_per_day': 2.0,
        'profile_completeness': 50.0,
        'avg_likes': 0.0,
        'avg_comments': 0.0,
        'archetype': 'EDGE_CASE'
    })
    
    # Very new
    accounts.append({
        'username': 'edge_very_new',
        'age_days': 1,
        'followers': 5,
        'following': 10,
        'posts_per_day': 1.0,
        'profile_completeness': 70.0,
        'avg_likes': 0.5,
        'avg_comments': 0.1,
        'archetype': 'EDGE_CASE'
    })
    
    # Perfect profile
    accounts.append({
        'username': 'edge_perfect',
        'age_days': 1000,
        'followers': 5000,
        'following': 500,
        'posts_per_day': 2.0,
        'profile_completeness': 100.0,
        'avg_likes': 500.0,
        'avg_comments': 50.0,
        'archetype': 'EDGE_CASE'
    })
    
    # Extremely high posting
    accounts.append({
        'username': 'edge_high_posting',
        'age_days': 10,
        'followers': 20,
        'following': 5000,
        'posts_per_day': 100.0,
        'profile_completeness': 30.0,
        'avg_likes': 0.5,
        'avg_comments': 0.1,
        'archetype': 'EDGE_CASE'
    })
    
    return accounts

def main():
    print("Generating synthetic dataset...")
    
    all_accounts = []
    all_accounts.extend(generate_normal_accounts(400))
    all_accounts.extend(generate_new_legitimate_accounts(150))
    all_accounts.extend(generate_suspicious_accounts(200))
    all_accounts.extend(generate_influencer_accounts(100))
    all_accounts.extend(generate_bot_like_accounts(80))
    all_accounts.extend(generate_incomplete_profile_accounts(40))
    all_accounts.extend(generate_low_engagement_accounts(30))
    all_accounts.extend(generate_edge_cases())
    
    # Shuffle accounts
    np.random.shuffle(all_accounts)
    
    # Create DataFrame
    df = pd.DataFrame(all_accounts)
    
    # Save to CSV
    output_path = '../data/synthetic_accounts.csv'
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(all_accounts)} synthetic accounts")
    print(f"Saved to {output_path}")
    print("\nDistribution by archetype:")
    print(df['archetype'].value_counts())

if __name__ == '__main__':
    main()