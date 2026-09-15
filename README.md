# FakeGuard - Social Media Account Risk Analyzer

**Problem Statement:** PS14 – Fake Social Media Account Risk Analyzer

A full-stack prototype system for analyzing synthetic social media account data to identify potential risk indicators and prioritize manual review.

## 🎯 Overview

FakeGuard is a decision-support tool that helps human reviewers prioritize their work by analyzing social media account profiles and activity patterns. It provides:

- **Explainable risk scoring** from 0-100
- **Four risk categories:** LOW, MEDIUM, HIGH, CRITICAL
- **Feature-by-feature breakdown** showing how each metric contributes
- **Reason codes** explaining specific risk indicators
- **Dashboard analytics** for reviewing account populations
- **CSV import** for batch processing

**Important:** This is a prototype using synthetic data for demonstration purposes. It does NOT:
- Access real social media platforms
- Make final determinations about account authenticity
- Replace human review

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- React Router
- Recharts
- CSS Modules

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pandas
- SQLite

### Project Structure

```
fakeguard/
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── styles/
│   └── package.json
│
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routes/
│   │   ├── scoring/
│   │   ├── models.py
│   │   └── main.py
│   ├── scripts/
│   ├── data/
│   ├── tests/
│   └── requirements.txt
│
└── docs/
```

## 📊 Scoring Methodology

### Feature Weights

| Feature | Weight | Description |
|---------|--------|-------------|
| Account Age | 20% | How long the account has existed |
| Follower/Following Ratio | 25% | Relationship between followers and following |
| Posting Frequency | 20% | Average posts per day |
| Profile Completeness | 15% | How complete the profile information is |
| Engagement | 20% | Average likes and comments relative to followers |

### Risk Categories

- **LOW (0-29.9):** No immediate action
- **MEDIUM (30-59.9):** Monitor account
- **HIGH (60-79.9):** Manual review recommended
- **CRITICAL (80-100):** Priority investigation

### Missing Data Handling

When metrics cannot be calculated (e.g., engagement when followers = 0), the feature is marked unavailable and the remaining features are renormalized. This prevents artificially inflating risk scores due to missing data.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Generate synthetic data:
```bash
python scripts/generate_synthetic_data.py
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend build:
```bash
cd frontend
npm run build
```

## 📱 Features

### Dashboard
- Total account statistics
- Risk category distribution
- Risk distribution pie chart
- Top priority accounts table

### Analyzer
- Real-time account analysis
- Interactive form with validation
- Risk gauge visualization
- Feature-by-feature breakdown
- Reason codes with explanations

### Accounts
- Paginated account list
- Search by username
- Filter by risk category
- Sortable columns
- CSV bulk import
- View individual account details

### Account Details
- Complete account information
- Latest analysis results
- Re-analyze functionality
- Historical analysis tracking

### Scoring Methodology
- Feature weights and thresholds
- Risk category definitions
- Reason code explanations
- Missing data handling
- Important disclaimers

## 🧪 Synthetic Dataset

The system includes 1,000+ synthetic accounts covering:

- **Normal accounts (400):** Typical legitimate users
- **New legitimate accounts (150):** Recently created but authentic
- **Suspicious accounts (200):** Bot-like behavior patterns
- **Influencers (100):** High-engagement legitimate accounts
- **Bot-like accounts (80):** Obvious automation patterns
- **Incomplete profiles (40):** Missing information
- **Low engagement (30):** Legitimate but inactive
- **Edge cases (6):** Zero followers, zero following, etc.

## 📖 API Endpoints

### Analysis
- `POST /api/analyze` - Analyze new account
- `POST /api/accounts/{id}/analyze` - Analyze existing account
- `GET /api/accounts/{id}/analysis` - Get analysis history

### Accounts
- `GET /api/accounts` - List accounts (pagination, search, filter, sort)
- `GET /api/accounts/{id}` - Get specific account
- `POST /api/accounts` - Create account

### Dashboard
- `GET /api/dashboard/summary` - Dashboard statistics
- `GET /api/dashboard/distribution` - Risk distribution
- `GET /api/dashboard/top-risk` - High-risk accounts

### Import
- `POST /api/import/csv` - Import accounts from CSV

### Configuration
- `GET /api/config/scoring` - Get scoring methodology
- `GET /api/health` - Health check

## 🎭 SIH Demo Workflow

1. **Start with Dashboard:** Show overall statistics and risk distribution
2. **Navigate to Analyzer:** Demonstrate live analysis with example inputs
3. **Analyze normal account:** Show LOW risk result
4. **Analyze suspicious account:** Show HIGH/CRITICAL risk with reason codes
5. **Analyze edge case:** Demonstrate zero followers handling
6. **View Accounts page:** Show search, filter, and sort functionality
7. **View Account Details:** Deep dive into specific account analysis
8. **Show Methodology page:** Explain scoring system to judges
9. **Discuss human-in-the-loop:** Emphasize decision support, not automation
10. **Mention future scope:** ML integration, additional signals, etc.

## ⚠️ Important Disclaimers

### Prototype Nature
The scoring weights and thresholds are prototype heuristics intended for demonstration and evaluation. They are not official government, law-enforcement, or social-media-platform standards.

### Synthetic Data Only
This prototype uses entirely synthetic/demo data. It does NOT:
- Scrape real social media platforms
- Access real user data
- Implement authentication bypass
- Violate platform terms of service

### Human Review Required
FakeGuard is a decision-support tool. All risk assessments require human review. The system:
- Does NOT make final determinations
- Does NOT replace human judgment
- Does NOT take automated punitive actions

## 🔮 Future Scope

### Machine Learning Integration
- Isolation Forest for anomaly detection
- Behavioral pattern clustering
- Temporal analysis
- Network analysis

### Additional Signals
- Content quality analysis
- Interaction patterns
- Time-based behavioral signals
- Cross-platform correlation

### Enhanced Capabilities
- Real-time monitoring
- Automated alert system
- Explainable AI integration
- Multi-language support

## 🛡️ Security Considerations

- Input validation on all endpoints
- No sensitive data exposure
- Proper error handling
- SQL injection prevention
- CORS configuration
- Rate limiting (recommended for production)

## 📄 License

This is a prototype developed for Smart India Hackathon 2024.

## 👥 Team

[Add your team information here]

## 📞 Contact

[Add contact information here]

---

**Remember:** This tool assists human reviewers. Final decisions about account authenticity must be made by trained personnel with appropriate legal authority and due process.