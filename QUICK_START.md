"# FakeGuard - Quick Start Guide

Get the system running in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- Terminal/Command Prompt

## Step 1: Start Backend (2 minutes)

```bash
# Open terminal 1
cd backend

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings pandas python-multipart pytest pytest-asyncio httpx python-dotenv

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at http://localhost:8000  
✅ API docs at http://localhost:8000/docs

## Step 2: Start Frontend (2 minutes)

```bash
# Open terminal 2
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

✅ Frontend running at http://localhost:5173

## Step 3: Import Data (1 minute)

1. Open http://localhost:5173
2. Click \"Accounts\" in navigation
3. Click \"Choose CSV File\"
4. Select `backend/data/synthetic_accounts.csv`
5. Click \"Import\"
6. Wait for \"Imported: 1006\" message

✅ Data loaded!

## Step 4: Explore

- **Dashboard:** View statistics and charts
- **Analyzer:** Try analyzing accounts
- **Accounts:** Browse, search, filter
- **Methodology:** Learn how scoring works

## Quick Test

**Navigate to Analyzer and test:**

**Normal Account:**
- Username: `demo_normal`
- Age: 500, Followers: 2000, Following: 1500
- Posts/day: 3.5, Profile: 90, Likes: 120, Comments: 15
- **Expected: LOW RISK**

**Suspicious Account:**
- Username: `demo_bot`
- Age: 5, Followers: 20, Following: 5000
- Posts/day: 75, Profile: 25, Likes: 1, Comments: 0.2
- **Expected: CRITICAL RISK**

## Verify Tests

```bash
cd backend
python -m pytest tests/ -v
```

Should show: **24 passed** ✅

## Build Production

```bash
cd frontend
npm run build
```

Should complete successfully ✅

## Troubleshooting

**Port already in use:**
```bash
# Backend - use different port
uvicorn app.main:app --reload --port 8001

# Frontend - Vite will auto-increment
```

**Import fails:**
- Ensure backend is running
- Check console for errors
- Verify CSV file path

**Tests fail:**
- Ensure in backend directory
- Check Python version (3.11+)
- Reinstall dependencies

## Next Steps

- Read `README.md` for detailed documentation
- Check `docs/demo-guide.md` for presentation walkthrough
- Review `docs/scoring-methodology.md` for scoring details
- Explore `docs/architecture.md` for system design

## Need Help?

All documentation is in:
- `README.md` - Main documentation
- `docs/` - Detailed guides
- `PROJECT_COMPLETION_REPORT.md` - Full project status

---

**System Status:** ✅ READY FOR DEMO"