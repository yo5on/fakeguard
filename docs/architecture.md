"# FakeGuard Architecture

## System Overview

FakeGuard is a full-stack web application designed to analyze social media account profiles and identify potential risk indicators for manual review prioritization.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Dashboard  │  │   Analyzer   │  │    Accounts      │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│                           │                                  │
│                    API Service Layer                         │
└───────────────────────────┼──────────────────────────────────┘
                            │
                     REST API (HTTP/JSON)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Routes                         │   │
│  │  /api/analyze  /api/accounts  /api/dashboard        │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │              Risk Scoring Engine                     │   │
│  │  - Feature calculation                               │   │
│  │  - Risk scoring                                      │   │
│  │  - Weighted aggregation                              │   │
│  │  - Reason code generation                            │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │            Database Layer (SQLAlchemy)               │   │
│  └──────────────────┬───────────────────────────────────┘   │
└────────────────────┼────────────────────────────────────────┘
                     │
              ┌──────▼─────┐
              │  SQLite DB │
              └────────────┘
```

## Component Architecture

### Frontend Components

```
frontend/
├── components/          # Reusable UI components
│   ├── Header.tsx      # Navigation header
│   ├── RiskGauge.tsx   # Visual risk score display
│   ├── RiskBadge.tsx   # Risk category badge
│   ├── RiskBreakdown.tsx    # Feature breakdown visualization
│   ├── ReasonList.tsx       # Risk reason codes
│   ├── StatCard.tsx         # Dashboard statistics
│   ├── LoadingState.tsx     # Loading indicator
│   ├── ErrorState.tsx       # Error handling
│   └── EmptyState.tsx       # Empty data state
│
├── pages/              # Application pages
│   ├── Dashboard.tsx        # Main dashboard
│   ├── Analyzer.tsx         # Account analysis form
│   ├── Accounts.tsx         # Account listing
│   ├── AccountDetails.tsx   # Individual account view
│   └── ScoringMethodology.tsx  # Methodology documentation
│
├── services/           # API integration
│   └── api.ts               # HTTP client
│
└── types/              # TypeScript definitions
    └── index.ts
```

### Backend Components

```
backend/
├── routes/                  # API endpoints
│   ├── analysis.py         # Analysis endpoints
│   ├── accounts.py         # Account CRUD
│   ├── dashboard.py        # Dashboard data
│   └── import_data.py      # CSV import
│
├── scoring/                 # Risk scoring logic
│   ├── risk_engine.py      # Main scoring engine
│   ├── feature_rules.py    # Feature calculation
│   └── reason_codes.py     # Reason generation
│
├── models.py               # Database models
├── schemas.py              # Pydantic schemas
└── database.py             # Database connection
```

## Data Flow

### Account Analysis Flow

1. **User Input**
   - User enters account data via Analyzer form
   - Frontend validates input fields

2. **API Request**
   - POST /api/analyze with account data
   - Backend validates using Pydantic schemas

3. **Feature Calculation**
   - Calculate account age risk
   - Calculate follower/following ratio risk
   - Calculate posting frequency risk
   - Calculate profile completeness risk
   - Calculate engagement risk

4. **Risk Scoring**
   - Apply feature weights
   - Handle missing features (renormalization)
   - Calculate weighted contributions
   - Compute final risk score (0-100)

5. **Category Assignment**
   - Determine risk category (LOW/MEDIUM/HIGH/CRITICAL)
   - Generate recommended action
   - Generate reason codes

6. **Response**
   - Return analysis result to frontend
   - Frontend visualizes results

### Dashboard Data Flow

1. **Load Dashboard**
   - Frontend requests dashboard data
   - Parallel API calls:
     - GET /api/dashboard/summary
     - GET /api/dashboard/distribution
     - GET /api/dashboard/top-risk

2. **Backend Processing**
   - Query database for latest analyses
   - Aggregate statistics
   - Calculate distributions
   - Sort top risk accounts

3. **Visualization**
   - Display statistics in cards
   - Render distribution chart
   - Show priority accounts table

## Database Schema

### accounts Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String | Account username |
| age_days | Integer | Account age in days |
| followers | Integer | Follower count |
| following | Integer | Following count |
| posts_per_day | Float | Average posts per day |
| profile_completeness | Float | Profile completion % |
| avg_likes | Float | Average likes per post |
| avg_comments | Float | Average comments per post |
| archetype | String | Synthetic data label (optional) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record update timestamp |

### analyses Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| account_id | Integer | Foreign key to accounts |
| risk_score | Float | Calculated risk score |
| category | String | Risk category |
| recommended_action | String | Recommended action |
| analysis_json | Text | Full analysis details (JSON) |
| created_at | DateTime | Analysis timestamp |

## Security Considerations

### Input Validation

- All inputs validated using Pydantic schemas
- Reject negative values
- Enforce profile_completeness range (0-100)
- Prevent SQL injection via parameterized queries

### Error Handling

- Never expose stack traces to frontend
- Generic error messages for users
- Detailed logging on backend
- Proper HTTP status codes

### CORS Configuration

- Configurable allowed origins
- Environment-based configuration
- Restricted to known frontends

### Data Safety

- No real social media data
- Synthetic data only
- No authentication/authorization for prototype
- No sensitive data storage

## Deployment Architecture

### Development

- Frontend: `npm run dev` (Vite dev server, port 5173)
- Backend: `uvicorn app.main:app --reload` (port 8000)
- Database: Local SQLite file

### Production (Planned)

- Frontend: Vercel or Netlify
- Backend: Render or Railway
- Database: Persistent SQLite or PostgreSQL
- Environment variables for configuration

## Performance Considerations

- Frontend code splitting (considered for future)
- Database indexing on username, account_id
- Efficient SQL queries with pagination
- API response caching (future enhancement)

## Scalability

Current prototype limitations:
- SQLite single-file database
- No horizontal scaling
- In-memory scoring engine

Future improvements:
- PostgreSQL for concurrent access
- Redis caching layer
- Background job processing for bulk imports
- Microservices architecture if needed

## Testing Strategy

### Backend Testing

- Unit tests for feature rules
- Integration tests for risk engine
- API endpoint tests
- Edge case coverage (zero values, missing data)

### Frontend Testing

- Build verification
- Manual integration testing
- Browser compatibility testing

### End-to-End Testing

- Complete user workflows
- CSV import validation
- Dashboard data accuracy
- Analysis result consistency

## Technology Choices

### Why FastAPI?

- Built-in OpenAPI documentation
- Pydantic validation
- Async support
- Modern Python framework

### Why React + TypeScript?

- Type safety
- Component reusability
- Strong ecosystem
- Developer experience

### Why SQLite?

- Zero configuration
- File-based portability
- Sufficient for prototype
- Easy GitHub integration

### Why Vite?

- Fast development server
- Modern build tool
- Excellent HMR
- Optimized production builds"