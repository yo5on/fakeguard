# FakeGuard Backend API

FastAPI backend for the Social Media Account Risk Analyzer.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file:
```bash
cp .env.example .env
```

4. Generate synthetic data:
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

Run with coverage:
```bash
pytest --cov=app tests/
```

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
- `GET /api/accounts` - List accounts (with pagination, search, filtering)
- `GET /api/accounts/{id}` - Get specific account
- `POST /api/accounts` - Create account

### Dashboard
- `GET /api/dashboard/summary` - Get dashboard statistics
- `GET /api/dashboard/distribution` - Get risk distribution
- `GET /api/dashboard/top-risk` - Get high-risk accounts

### Import
- `POST /api/import/csv` - Import accounts from CSV

### Configuration
- `GET /api/config/scoring` - Get scoring methodology
- `GET /api/health` - Health check