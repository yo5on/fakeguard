"# FakeGuard - SIH Demo Guide

This guide provides a complete walkthrough for demonstrating FakeGuard during the Smart India Hackathon presentation.

## Pre-Demo Setup Checklist

### Backend Setup

1. Ensure backend dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

2. Verify synthetic data exists:
```bash
ls data/synthetic_accounts.csv
```

3. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Verify backend is running:
- Open http://localhost:8000/docs
- Check API documentation loads
- Test GET /api/health endpoint

### Frontend Setup

1. Ensure frontend dependencies are installed:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Verify frontend is running:
- Open http://localhost:5173
- Check dashboard loads
- Verify no console errors

### Data Import

Import the synthetic dataset:

1. Navigate to Accounts page
2. Click \"Choose CSV File\"
3. Select `backend/data/synthetic_accounts.csv`
4. Click \"Import\"
5. Verify import success (should show ~1000 imported accounts)
6. Return to Dashboard to see populated statistics

## Demo Flow

### Part 1: Problem Statement (2 minutes)

**Script:**
> \"Social media platforms face a critical challenge: identifying fake or suspicious accounts at scale. Manual review is time-consuming, and automated systems lack transparency. Our solution, FakeGuard, is a decision-support tool that helps human reviewers prioritize their work using explainable risk scoring.\"

**Key Points:**
- Emphasize human-in-the-loop approach
- Mention transparency and explainability
- Clarify it's decision support, not autonomous enforcement

### Part 2: Dashboard Overview (3 minutes)

**Navigate to:** Dashboard (`/dashboard`)

**Demonstrate:**

1. **Statistics Cards** (top section)
   - Point out total accounts analyzed
   - Show distribution across risk categories
   - Highlight average risk score

2. **Risk Distribution Chart** (left section)
   - Explain visual representation of risk categories
   - Show balanced distribution (not all HIGH or all LOW)

3. **Priority Review Table** (right section)
   - Point out highest-risk accounts listed first
   - Show risk scores and categories
   - Explain this helps reviewers focus on priorities

**Script:**
> \"The dashboard provides an at-a-glance view of the account population. Reviewers can immediately see how many accounts require attention and where to focus their efforts.\"

### Part 3: Account Analysis (5 minutes)

**Navigate to:** Analyzer (`/analyzer`)

#### Demo 3A: Normal Account

**Input:**
- Username: `demo_normal_user`
- Age (days): 500
- Followers: 2000
- Following: 1500
- Posts per day: 3.5
- Profile completeness: 90
- Avg likes: 120
- Avg comments: 15

**Expected Result:** LOW RISK

**Points to Highlight:**
- Risk gauge shows green/low score
- All features contribute minimally
- No significant reason codes
- Recommended action: \"No immediate action\"

**Script:**
> \"Here's a typical legitimate account. Notice how each feature is evaluated independently, and the system explains why this account is low risk.\"

#### Demo 3B: Suspicious Account

**Input:**
- Username: `demo_suspicious_bot`
- Age (days): 5
- Followers: 20
- Following: 5000
- Posts per day: 75
- Profile completeness: 25
- Avg likes: 1
- Avg comments: 0.2

**Expected Result:** CRITICAL RISK

**Points to Highlight:**
- Risk gauge shows red/critical score
- Multiple red flags in feature breakdown
- Several reason codes generated (R01, R02, R03, R04, R05)
- Recommended action: \"Priority investigation\"

**Script:**
> \"This account exhibits multiple bot-like behaviors: it's brand new, follows thousands but has few followers, posts excessively, has an incomplete profile, and gets minimal engagement. Each of these contributes to the high risk score, and the system explains exactly why.\"

#### Demo 3C: Edge Case - Zero Followers

**Input:**
- Username: `demo_edge_case`
- Age (days): 100
- Followers: 0
- Following: 0
- Posts per day: 2
- Profile completeness: 70
- Avg likes: 0
- Avg comments: 0

**Expected Result:** LOW to MEDIUM RISK

**Points to Highlight:**
- System does NOT crash
- Engagement and follower ratio marked as \"Unavailable\"
- Score calculated from remaining 3 features
- Renormalization explained in methodology

**Script:**
> \"Notice how the system handles missing data gracefully. When engagement can't be calculated because there are zero followers, the system marks it unavailable and recalculates the score using only the remaining features. It doesn't assume maximum risk.\"

### Part 4: Feature Breakdown Deep Dive (3 minutes)

**Using the suspicious account result from Demo 3B:**

**Demonstrate:**

1. **Feature-by-Feature Breakdown**
   - Show individual feature risk scores
   - Point out weighted contributions
   - Explain color-coded progress bars

2. **Reason Codes**
   - Show sorted list (highest contribution first)
   - Read code descriptions
   - Explain how they help reviewers understand the score

3. **Transparency**
   - Scroll to disclaimer
   - Emphasize prototype nature
   - Mention human review requirement

**Script:**
> \"Every decision is explainable. Reviewers can see exactly which features contributed to the risk score and by how much. This transparency is crucial for accountability and trust in the system.\"

### Part 5: Account Management (3 minutes)

**Navigate to:** Accounts (`/accounts`)

**Demonstrate:**

1. **Search Functionality**
   - Search for \"suspicious\"
   - Show filtered results

2. **Category Filtering**
   - Select \"HIGH\" from dropdown
   - Show only high-risk accounts

3. **Sorting**
   - Click column headers to sort
   - Show sorting by risk score
   - Sort by followers descending

4. **Pagination**
   - Show page navigation
   - Demonstrate moving between pages

**Script:**
> \"Reviewers can quickly find specific accounts, filter by risk category, and sort by various metrics to prioritize their workflow.\"

### Part 6: Individual Account View (2 minutes)

**Action:** Click on any HIGH or CRITICAL risk account

**Demonstrate:**

1. **Account Information Panel**
   - Show all account metrics in one place
   - Point out clean, organized layout

2. **Latest Analysis Section**
   - Show full analysis results
   - Risk gauge, category, breakdown, reasons

3. **Re-analyze Button**
   - Click \"Re-analyze Account\"
   - Show analysis updating
   - Explain historical tracking (analyses are not overwritten)

**Script:**
> \"Each account has a dedicated detail page showing all information and analysis results. Reviewers can re-analyze accounts at any time, and all analysis history is preserved.\"

### Part 7: Scoring Methodology (2 minutes)

**Navigate to:** Methodology (`/scoring`)

**Demonstrate:**

1. **Feature Weights**
   - Scroll through each feature
   - Show thresholds and formulas

2. **Risk Categories**
   - Show category definitions
   - Point out score ranges

3. **Reason Codes**
   - List all codes and descriptions

4. **Disclaimer**
   - Read the disclaimer section
   - Emphasize prototype nature

**Script:**
> \"Complete transparency is built into the system. Anyone can view the exact methodology, weights, and thresholds used. This page serves as documentation for reviewers and auditors.\"

### Part 8: CSV Import (1 minute)

**Navigate back to:** Accounts

**Demonstrate:**

1. **CSV Import Feature**
   - Show file upload interface
   - Explain batch processing capability
   - Point out import results (imported/skipped/errors)

**Script:**
> \"Organizations can bulk-import accounts from CSV files for batch analysis. The system validates data, reports errors, and handles duplicates gracefully.\"

### Part 9: Technical Architecture (2 minutes)

**Open backend API docs:** http://localhost:8000/docs

**Demonstrate:**

1. **API Documentation**
   - Show auto-generated OpenAPI docs
   - Point out available endpoints
   - Expand a few endpoints to show schemas

2. **Tech Stack Highlight**
   - Frontend: React + TypeScript + Vite
   - Backend: FastAPI + Python
   - Database: SQLite
   - Charts: Recharts

**Script:**
> \"The system is built with modern, industry-standard technologies. FastAPI provides automatic API documentation, Pydantic ensures data validation, and React creates a responsive user interface.\"

### Part 10: Testing and Reliability (2 minutes)

**Open terminal and run tests:**

```bash
cd backend
pytest tests/ -v
```

**Show:**
- All tests passing
- Feature rule tests
- Risk engine tests
- API integration tests
- Edge case coverage

**Script:**
> \"The system includes comprehensive automated tests covering feature calculation, risk scoring, edge cases like zero values, and API endpoints. All 24 tests pass, demonstrating reliability.\"

### Part 11: Future Scope (2 minutes)

**Discuss:**

1. **Machine Learning Integration**
   - Isolation Forest for anomaly detection
   - Supervised learning with labeled data
   - Behavioral pattern analysis

2. **Additional Features**
   - Content analysis (text, images)
   - Network graph analysis
   - Temporal behavioral patterns
   - Cross-platform correlation

3. **Production Enhancements**
   - Real-time monitoring
   - Alert system for new critical accounts
   - Multi-user support with role-based access
   - Audit logging
   - Performance optimization for millions of accounts

**Script:**
> \"While the current system uses rule-based scoring, future versions could incorporate machine learning for anomaly detection while maintaining explainability. Additional signals like content analysis and network connections could further improve accuracy.\"

### Part 12: Q&A Preparation

**Expected Questions and Answers:**

**Q: How accurate is the system?**
A: This is a prototype demonstrating the approach. Accuracy depends on threshold tuning and would require validation against labeled real-world data. The current weights are heuristic estimates for demonstration.

**Q: Can this detect all fake accounts?**
A: No system can detect all fake accounts with 100% accuracy. This tool helps prioritize manual review by flagging suspicious patterns. Human reviewers make final decisions.

**Q: What about false positives?**
A: False positives are a concern in any automated system. That's why we emphasize human review. The explainability features help reviewers understand and validate each flag.

**Q: Why not use machine learning?**
A: Rule-based systems provide transparency and explainability, which are crucial for accountability. ML can be added later as an additional signal while maintaining the explainable core.

**Q: Does this violate user privacy?**
A: This prototype only uses synthetic data. In production, it would only analyze publicly visible profile information, not private messages or personal data. It respects platform terms of service.

**Q: How does this scale?**
A: The current SQLite database is suitable for demonstration. Production deployment would use PostgreSQL or similar for concurrent access and horizontal scaling.

**Q: Can this work with different social media platforms?**
A: The feature framework is platform-agnostic. Specific thresholds and weights might need adjustment per platform, but the core logic applies broadly.

## Demo Tips

### Timing

- Total demo: 25 minutes
- Leave 5 minutes for questions
- Practice to stay within time

### Presentation Style

- Speak clearly and at a moderate pace
- Use the script as a guide, not a strict reading
- Make eye contact with judges
- Show enthusiasm for the project

### Technical Preparation

- Test everything before the demo
- Have backup plan if internet fails (local works)
- Keep terminal windows organized
- Have API docs pre-loaded in a tab

### Emphasis Points

1. **Human-in-the-loop:** Repeat multiple times
2. **Explainability:** Show feature breakdown several times
3. **Prototype nature:** Be honest about limitations
4. **Real-world applicability:** Connect to actual problems

### What NOT to Say

- \"This detects all fake accounts\"
- \"100% accurate\"
- \"Better than existing systems\" (without proof)
- \"Ready for production\" (it's a prototype)
- Any claims about real platforms or real data

## Post-Demo

### Handover Materials

Prepare to provide:
- GitHub repository link
- README with setup instructions
- Architecture documentation
- API documentation export
- Slide deck (if prepared)

### Follow-up Questions

Be prepared to discuss:
- Implementation timeline
- Team roles and contributions
- Challenges faced and overcome
- Learning outcomes
- Future development plans

## Success Metrics for Demo

- Judges understand the human-in-the-loop concept
- Explainability is clearly demonstrated
- Technical competence is evident
- System runs smoothly without crashes
- Questions answered confidently
- Time management executed well

## Emergency Troubleshooting

### Backend Not Starting
```bash
# Check if port 8000 is in use
netstat -an | findstr :8000

# Kill process if needed, then restart
uvicorn app.main:app --reload --port 8001
```

### Frontend Not Starting
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database Issues
```bash
# Regenerate database
rm backend/fakeguard.db
cd backend
python scripts/generate_synthetic_data.py
# Re-import CSV via UI
```

### Import Not Working
- Check CSV file path
- Verify backend is running
- Check browser console for errors
- Refresh page and try again

Good luck with your presentation!"