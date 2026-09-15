# FakeGuard Production Deployment Guide

## Overview

This guide will help you deploy FakeGuard to production hosting:
- **Frontend:** Vercel
- **Backend:** Render
- **Database:** SQLite (with persistence considerations)

---

## Prerequisites

- GitHub account with access to `https://github.com/yo5on/fakeguard`
- Vercel account (free tier works)
- Render account (free tier works)

---

## Step 1: Deploy Backend to Render

### 1.1 Create Render Account

1. Go to https://render.com
2. Sign up or log in (you can use GitHub authentication)

### 1.2 Create Web Service

1. Click **"New +"** button in the top right
2. Select **"Web Service"**
3. Connect your GitHub account if prompted
4. Select the repository: `yo5on/fakeguard`
5. Click **"Connect"**

### 1.3 Configure Service

Enter the following settings:

**Basic Settings:**
- **Name:** `fakeguard-backend` (or your preferred name)
- **Region:** Choose closest to your target users
- **Branch:** `master`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **Free** tier (sufficient for prototype)

### 1.4 Add Environment Variables

Scroll down to **Environment Variables** section and add:

| Key | Value |
|-----|-------|
| `CORS_ORIGINS` | `*` |
| `DATABASE_URL` | `sqlite:///./fakeguard.db` |

**Note:** We'll update `CORS_ORIGINS` after deploying the frontend.

### 1.5 Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for the first deployment
3. Watch the logs for any errors
4. Once deployed, you'll see a green **"Live"** indicator

### 1.6 Get Backend URL

Your backend URL will be:
```
https://fakeguard-backend.onrender.com
```

**Or with your custom name:**
```
https://your-service-name.onrender.com
```

### 1.7 Test Backend

Open in browser or use curl:
```bash
curl https://your-backend-url.onrender.com/api/health
```

Expected response:
```json
{"status":"healthy","service":"fakeguard-api"}
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account

1. Go to https://vercel.com
2. Sign up or log in (recommend using GitHub authentication)

### 2.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Import Git Repository
3. Select `yo5on/fakeguard` from GitHub
4. Click **"Import"**

### 2.3 Configure Project

**Framework Preset:**
- Should auto-detect as **"Vite"**

**Root Directory:**
- Click **"Edit"** next to Root Directory
- Enter: `frontend`
- Click **"Continue"**

**Build Settings:**
- **Build Command:** `npm run build` (auto-filled)
- **Output Directory:** `dist` (auto-filled)
- **Install Command:** `npm install` (auto-filled)

### 2.4 Add Environment Variables

Expand **"Environment Variables"** section:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://your-backend-url.onrender.com` |

**Important:** Replace `your-backend-url.onrender.com` with your actual Render backend URL from Step 1.6.

### 2.5 Deploy

1. Click **"Deploy"**
2. Wait 2-5 minutes for deployment
3. Watch build logs for any errors
4. Once deployed, you'll see a success screen with a preview

### 2.6 Get Frontend URL

Your frontend URL will be:
```
https://fakeguard-xxxx.vercel.app
```

Click **"Visit"** or **"Continue to Dashboard"** to see your URL.

---

## Step 3: Update Backend CORS

Now that you have the Vercel frontend URL, update the backend:

### 3.1 Update Environment Variable

1. Go back to **Render Dashboard**
2. Click on your `fakeguard-backend` service
3. Go to **"Environment"** tab in the left sidebar
4. Find `CORS_ORIGINS` variable
5. Click **"Edit"**
6. Change value from `*` to your Vercel URL:
   ```
   https://fakeguard-xxxx.vercel.app
   ```
7. Click **"Save Changes"**

### 3.2 Automatic Redeployment

Render will automatically redeploy with the new CORS settings (takes 2-3 minutes).

---

## Step 4: Seed Synthetic Data

**Important:** Render's free tier uses ephemeral storage, meaning the SQLite database will be reset on each deployment. You need to import the synthetic data after deployment.

### 4.1 Import Data via UI

1. Open your deployed frontend: `https://fakeguard-xxxx.vercel.app`
2. Navigate to **"Accounts"** page (top navigation)
3. Look for the CSV import section
4. Click **"Choose CSV File"**
5. Navigate to your local repository: `backend/data/synthetic_accounts.csv`
6. Select the file
7. Click **"Import"**
8. Wait for the import to complete (should show "Imported: 1006")

### 4.2 Verify Data Loaded

1. Go to **"Dashboard"** page
2. Verify statistics show:
   - Total Accounts: 1006
   - Risk categories populated
   - Charts displaying data

---

## Step 5: Verification Checklist

### Backend Health Checks

Test these endpoints in your browser:

✅ **Health Check:**
```
https://your-backend-url.onrender.com/api/health
```

✅ **Scoring Config:**
```
https://your-backend-url.onrender.com/api/config/scoring
```

✅ **Dashboard Summary:**
```
https://your-backend-url.onrender.com/api/dashboard/summary
```

### Frontend Verification

Test these flows in the deployed frontend:

✅ **Dashboard**
- Statistics load correctly
- Risk distribution chart displays
- Priority accounts table shows data

✅ **Analyzer**
- Form accepts input
- Analysis returns results
- Risk score, category, and reasons display

✅ **Accounts**
- Account list loads
- Search works
- Filtering by category works
- Sorting works
- Pagination works

✅ **Account Details**
- Clicking an account shows details
- Latest analysis displays
- Re-analyze button works

✅ **Methodology**
- Page loads with scoring information

✅ **Browser Console**
- No errors in console (F12 → Console tab)
- No failed network requests

---

## Step 6: Post-Deployment Configuration

### 6.1 Custom Domain (Optional)

**Vercel:**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

**Render:**
1. Go to Service Settings → Custom Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### 6.2 Update CORS After Custom Domain

If you add a custom domain to Vercel:
1. Update `CORS_ORIGINS` in Render to include the custom domain
2. Example: `https://fakeguard.yourdomain.com`

---

## Troubleshooting

### Backend Issues

**Problem:** Backend shows "Application failed to respond"
- **Solution:** Check Render logs for Python errors
- **Solution:** Verify `requirements.txt` is correct
- **Solution:** Ensure start command is correct

**Problem:** CORS errors in browser console
- **Solution:** Verify `CORS_ORIGINS` matches your Vercel URL exactly
- **Solution:** Include protocol (`https://`)
- **Solution:** No trailing slash

**Problem:** Database is empty after redeployment
- **Expected:** This is normal on Render's free tier
- **Solution:** Re-import CSV after each deployment
- **Alternative:** Upgrade to Render paid tier for persistent storage

### Frontend Issues

**Problem:** Build fails during deployment
- **Solution:** Check Vercel build logs
- **Solution:** Verify `package.json` is correct
- **Solution:** Ensure all dependencies are listed

**Problem:** API calls fail with 404
- **Solution:** Verify `VITE_API_URL` environment variable is set correctly
- **Solution:** Check that backend URL includes protocol (`https://`)
- **Solution:** Ensure no trailing `/api` in `VITE_API_URL`

**Problem:** Dashboard shows no data
- **Solution:** Import synthetic data (see Step 4)
- **Solution:** Check browser console for API errors
- **Solution:** Verify backend is running

---

## Important Notes for SIH Demo

### Database Persistence

⚠️ **Render Free Tier Limitation:**
- SQLite database is **ephemeral**
- Data is **lost on each deployment**
- Data **may be lost** if the service restarts after inactivity

**Recommendations:**
1. **Import data before demo:** Always re-import the CSV before your presentation
2. **Test before demo:** Verify data is present 10-15 minutes before presenting
3. **Keep backend active:** Visit the backend URL periodically to prevent cold starts
4. **Have backup plan:** Keep the local version running as backup

### Cold Starts

⚠️ **Render Free Tier Cold Starts:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- Subsequent requests are fast

**Recommendations:**
1. **Warm up before demo:** Visit the site 5 minutes before presenting
2. **Explain if needed:** Mention it's a free-tier demo if there's initial delay

---

## Upgrade Options (If Needed)

### For Production Use Beyond Demo

If you need persistence and better performance:

**Render:**
- Upgrade to **Starter Plan** ($7/month)
- Includes persistent disk storage
- No cold starts

**Database:**
- Migrate to PostgreSQL on Render
- Free PostgreSQL tier available
- Requires schema migration

**Vercel:**
- Free tier is sufficient for this project
- Pro plan ($20/month) adds analytics and more

---

## Deployment Commands Reference

### Backend Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Build Command
```bash
npm run build
```

### Frontend Output Directory
```
dist
```

---

## Environment Variables Summary

### Backend (Render)
```
CORS_ORIGINS=https://your-vercel-url.vercel.app
DATABASE_URL=sqlite:///./fakeguard.db
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-render-url.onrender.com
```

---

## Security Checklist

✅ No `.env` files committed to repository
✅ No API keys or secrets in code
✅ CORS properly configured (not `*` in production)
✅ HTTPS enabled (automatic on Vercel and Render)
✅ No database credentials exposed
✅ Synthetic data only (no real user data)

---

## Support & Resources

**Documentation:**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Vite Docs: https://vitejs.dev/guide/
- FastAPI Docs: https://fastapi.tiangolo.com/

**Dashboard Links:**
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard
- GitHub Repository: https://github.com/yo5on/fakeguard

---

## Quick Deploy Checklist

- [ ] Deploy backend to Render
- [ ] Get backend URL
- [ ] Deploy frontend to Vercel with `VITE_API_URL`
- [ ] Get frontend URL
- [ ] Update backend `CORS_ORIGINS`
- [ ] Import synthetic data (1006 accounts)
- [ ] Test all pages and features
- [ ] Verify browser console has no errors
- [ ] Warm up before demo
- [ ] Have local backup ready

---

**Last Updated:** 2026-09-15  
**Repository:** https://github.com/yo5on/fakeguard  
**Status:** Ready for deployment