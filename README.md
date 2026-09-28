<div align="center">

<img src="https://raw.githubusercontent.com/yo5on/yo5on/main/hd-projects.svg" width="620" alt="projects"/>

<samp><b>FAKEGUARD — SOCIAL MEDIA ACCOUNT RISK ANALYZER</b></samp>

<samp>python · fastapi · react · typescript · ai/ml</samp>

</div>

---

<div align="center"><samp>A full-stack prototype system for analyzing synthetic social media account data to identify potential risk indicators and prioritize manual review.</samp></div>

---

<div align="center"><samp><b>Project Overview</b></samp></div>

<samp>FakeGuard is a decision-support tool that helps human reviewers prioritize their work by analyzing social media account profiles and activity patterns. It provides:</samp>

- <samp><b>Explainable risk scoring</b> from 0-100</samp>
- <samp><b>Four risk categories:</b> LOW, MEDIUM, HIGH, CRITICAL</samp>
- <samp><b>Feature-by-feature breakdown</b> showing how each metric contributes</samp>
- <samp><b>Reason codes</b> explaining specific risk indicators</samp>
- <samp><b>Dashboard analytics</b> for reviewing account populations</samp>
- <samp><b>CSV import</b> for batch processing</samp>

<samp><b>Important:</b> This is a prototype using synthetic data for demonstration purposes. It does not access real social media platforms, make final determinations about account authenticity, or replace human review.</samp>

---

<div align="center"><samp><b>Architecture</b></samp></div>

<samp><b>Tech Stack</b></samp>

<samp><b>Frontend</b></samp>

- <samp>React 18 + TypeScript</samp>
- <samp>Vite</samp>
- <samp>React Router</samp>
- <samp>Recharts</samp>
- <samp>CSS Modules</samp>

<samp><b>Backend</b></samp>

- <samp>Python 3.11+</samp>
- <samp>FastAPI</samp>
- <samp>SQLAlchemy</samp>
- <samp>Pandas</samp>
- <samp>SQLite</samp>

<samp><b>Project Structure</b></samp>

```text
fakeguard/
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── styles/
│   └── package.json
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
└── docs/
```

---

<div align="center"><samp><b>Scoring Methodology</b></samp></div>

<samp><b>Feature Weights</b></samp>

| Feature | Weight | Description |
|---|---:|---|
| <samp>Account Age</samp> | <samp>20%</samp> | <samp>How long the account has existed</samp> |
| <samp>Follower/Following Ratio</samp> | <samp>25%</samp> | <samp>Relationship between followers and following</samp> |
| <samp>Posting Frequency</samp> | <samp>20%</samp> | <samp>Average posts per day</samp> |
| <samp>Profile Completeness</samp> | <samp>15%</samp> | <samp>How complete the profile information is</samp> |
| <samp>Engagement</samp> | <samp>20%</samp> | <samp>Average likes and comments relative to followers</samp> |

<samp><b>Risk Categories</b></samp>

- <samp><b>LOW (0-29.9):</b> No immediate action</samp>
- <samp><b>MEDIUM (30-59.9):</b> Monitor account</samp>
- <samp><b>HIGH (60-79.9):</b> Manual review recommended</samp>
- <samp><b>CRITICAL (80-100):</b> Priority investigation</samp>

<samp><b>Missing Data Handling</b></samp>

<samp>When metrics cannot be calculated (e.g., engagement when followers = 0), the feature is marked unavailable and the remaining features are renormalized. This prevents artificially inflating risk scores due to missing data.</samp>

---

<div align="center"><samp><b>Getting Started</b></samp></div>

<samp><b>Prerequisites</b></samp>

- <samp>Python 3.11+</samp>
- <samp>Node.js 18+</samp>
- <samp>Git</samp>

<samp><b>Backend Setup</b></samp>

1. <samp>Navigate to backend directory:</samp>

```bash
cd backend
```

2. <samp>Create virtual environment:</samp>

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. <samp>Install dependencies:</samp>

```bash
pip install -r requirements.txt
```

4. <samp>Generate synthetic data:</samp>

```bash
python scripts/generate_synthetic_data.py
```

5. <samp>Run the server:</samp>

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

<samp>API: http://localhost:8000</samp>

<samp>API documentation: http://localhost:8000/docs</samp>

<samp><b>Frontend Setup</b></samp>

```bash
cd frontend
npm install
npm run dev
```

<samp>Frontend: http://localhost:5173</samp>

<samp><b>Running Tests</b></samp>

```bash
cd backend
pytest
```

<samp><b>Frontend Build</b></samp>

```bash
cd frontend
npm run build
```

---

<div align="center"><samp><b>Features</b></samp></div>

<samp><b>Dashboard</b></samp>

- <samp>Total account statistics</samp>
- <samp>Risk category distribution</samp>
- <samp>Risk distribution pie chart</samp>
- <samp>Top priority accounts table</samp>

<samp><b>Analyzer</b></samp>

- <samp>Real-time account analysis</samp>
- <samp>Interactive form with validation</samp>
- <samp>Risk gauge visualization</samp>
- <samp>Feature-by-feature breakdown</samp>
- <samp>Reason codes with explanations</samp>

<samp><b>Accounts</b></samp>

- <samp>Paginated account list</samp>
- <samp>Search by username</samp>
- <samp>Filter by risk category</samp>
- <samp>Sortable columns</samp>
- <samp>CSV bulk import</samp>
- <samp>View individual account details</samp>

<samp><b>Account Details</b></samp>

- <samp>Complete account information</samp>
- <samp>Latest analysis results</samp>
- <samp>Re-analyze functionality</samp>
- <samp>Historical analysis tracking</samp>

<samp><b>Scoring Methodology</b></samp>

- <samp>Feature weights and thresholds</samp>
- <samp>Risk category definitions</samp>
- <samp>Reason code explanations</samp>
- <samp>Missing data handling</samp>
- <samp>Important disclaimers</samp>

---

<div align="center"><samp><b>Synthetic Dataset</b></samp></div>

<samp>The system includes 1,000+ synthetic accounts covering:</samp>

- <samp><b>Normal accounts (400):</b> Typical legitimate users</samp>
- <samp><b>New legitimate accounts (150):</b> Recently created but authentic</samp>
- <samp><b>Suspicious accounts (200):</b> Bot-like behavior patterns</samp>
- <samp><b>Influencers (100):</b> High-engagement legitimate accounts</samp>
- <samp><b>Bot-like accounts (80):</b> Obvious automation patterns</samp>
- <samp><b>Incomplete profiles (40):</b> Missing information</samp>
- <samp><b>Low engagement (30):</b> Legitimate but inactive</samp>
- <samp><b>Edge cases (6):</b> Zero followers, zero following, etc.</samp>

---

<div align="center"><samp><b>API Endpoints</b></samp></div>

<samp><b>Analysis</b></samp>

- <samp><code>POST /api/analyze</code> — Analyze new account</samp>
- <samp><code>POST /api/accounts/{id}/analyze</code> — Analyze existing account</samp>
- <samp><code>GET /api/accounts/{id}/analysis</code> — Get analysis history</samp>

<samp><b>Accounts</b></samp>

- <samp><code>GET /api/accounts</code> — List accounts (pagination, search, filter, sort)</samp>
- <samp><code>GET /api/accounts/{id}</code> — Get specific account</samp>
- <samp><code>POST /api/accounts</code> — Create account</samp>

<samp><b>Dashboard</b></samp>

- <samp><code>GET /api/dashboard/summary</code> — Dashboard statistics</samp>
- <samp><code>GET /api/dashboard/distribution</code> — Risk distribution</samp>
- <samp><code>GET /api/dashboard/top-risk</code> — High-risk accounts</samp>

<samp><b>Import</b></samp>

- <samp><code>POST /api/import/csv</code> — Import accounts from CSV</samp>

<samp><b>Configuration</b></samp>

- <samp><code>GET /api/config/scoring</code> — Get scoring methodology</samp>
- <samp><code>GET /api/health</code> — Health check</samp>

---

<div align="center"><samp><b>Tech Utsav Demo Workflow</b></samp></div>

1. <samp><b>Start with Dashboard:</b> Show overall statistics and risk distribution</samp>
2. <samp><b>Navigate to Analyzer:</b> Demonstrate live analysis with example inputs</samp>
3. <samp><b>Analyze normal account:</b> Show LOW risk result</samp>
4. <samp><b>Analyze suspicious account:</b> Show HIGH/CRITICAL risk with reason codes</samp>
5. <samp><b>Analyze edge case:</b> Demonstrate zero followers handling</samp>
6. <samp><b>View Accounts page:</b> Show search, filter, and sort functionality</samp>
7. <samp><b>View Account Details:</b> Deep dive into specific account analysis</samp>
8. <samp><b>Show Methodology page:</b> Explain scoring system to judges</samp>
9. <samp><b>Discuss human-in-the-loop:</b> Emphasize decision support, not automation</samp>
10. <samp><b>Mention future scope:</b> ML integration, additional signals, etc.</samp>

---

<div align="center"><samp><b>Important Disclaimers</b></samp></div>

<samp><b>Prototype Nature</b></samp>

<samp>The scoring weights and thresholds are prototype heuristics intended for demonstration and evaluation. They are not official government, law-enforcement, or social-media-platform standards.</samp>

<samp><b>Synthetic Data Only</b></samp>

<samp>This prototype uses entirely synthetic/demo data. It does not scrape real social media platforms, access real user data, implement authentication bypass, or violate platform terms of service.</samp>

<samp><b>Human Review Required</b></samp>

<samp>FakeGuard is a decision-support tool. All risk assessments require human review. The system does not make final determinations, replace human judgment, or take automated punitive actions.</samp>

---

<div align="center"><samp><b>Future Scope</b></samp></div>

<samp><b>Machine Learning Integration</b></samp>

- <samp>Isolation Forest for anomaly detection</samp>
- <samp>Behavioral pattern clustering</samp>
- <samp>Temporal analysis</samp>
- <samp>Network analysis</samp>

<samp><b>Additional Signals</b></samp>

- <samp>Content quality analysis</samp>
- <samp>Interaction patterns</samp>
- <samp>Time-based behavioral signals</samp>
- <samp>Cross-platform correlation</samp>

<samp><b>Enhanced Capabilities</b></samp>

- <samp>Real-time monitoring</samp>
- <samp>Automated alert system</samp>
- <samp>Explainable AI integration</samp>
- <samp>Multi-language support</samp>

---

<div align="center"><samp><b>Security Considerations</b></samp></div>

- <samp>Input validation on all endpoints</samp>
- <samp>No sensitive data exposure</samp>
- <samp>Proper error handling</samp>
- <samp>SQL injection prevention</samp>
- <samp>CORS configuration</samp>
- <samp>Rate limiting (recommended for production)</samp>

---

<div align="center"><samp><b>Event</b></samp></div>

<samp>Developed for <b>Tech Utsav</b> as a college hackathon project.</samp>

---

<div align="center"><samp><b>Team</b></samp></div>

<samp>Developed as a team project for Tech Utsav.</samp>

---

<div align="center"><samp><b>Contact</b></samp></div>

<samp>For questions or feedback, please open an issue in this repository.</samp>

---

<samp><b>Remember:</b> This tool assists human reviewers. Final decisions about account authenticity must be made by trained personnel with appropriate legal authority and due process.</samp>
