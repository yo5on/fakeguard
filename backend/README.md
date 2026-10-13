# FakeGuard Backend API

FastAPI backend for the Social Media Account Risk Analyzer.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies (`requirements.txt` holds runtime packages only; the dev file adds pytest and the data-generation tools):
```bash
pip install -r requirements-dev.txt
```

3. Optionally create a .env file (see `.env.example` for `DATABASE_URL`, `CORS_ORIGINS`, `MAX_UPLOAD_BYTES`):
```bash
cp .env.example .env
```

4. (Optional) Regenerate the synthetic dataset in `data/synthetic_accounts.csv`:
```bash
python scripts/generate_synthetic_data.py
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Run tests:
```bash
pytest
```

Tests use an in-memory SQLite database and never touch `fakeguard.db`.
`tests/test_regressions.py` covers bugs fixed during the code audit.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Analysis
- `POST /api/analyze` - Analyze a new account
- `POST /api/accounts/{id}/analyze` - Analyze existing account
- `GET /api/accounts/{id}/analysis` - Get analysis history

### Accounts
- `GET /api/accounts` - List accounts (`skip`, `limit` 1-100, `search`, `category`, `sort_by`, `sort_order`)
- `GET /api/accounts/{id}` - Get specific account
- `POST /api/accounts` - Create account

### Dashboard
- `GET /api/dashboard/summary` - Get dashboard statistics
- `GET /api/dashboard/distribution` - Get risk distribution
- `GET /api/dashboard/top-risk` - Get high-risk accounts (`limit` 1-100)

### Import
- `POST /api/import/csv` - Import accounts from a UTF-8 CSV (max 5 MB by default); each imported account gets an initial analysis

### Configuration
- `GET /api/config/scoring` - Get scoring methodology
- `GET /api/health` - Health check