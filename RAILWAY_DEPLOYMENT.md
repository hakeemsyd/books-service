# Railway Deployment Guide

This guide covers deploying the Books Service to [Railway.app](https://railway.app).

## Prerequisites

- GitHub account with the repository pushed
- Railway account (free tier available: https://railway.app)
- Git installed locally

## Why Railway?

✅ **Simple setup** - Connect GitHub, auto-deploy on push  
✅ **Free tier** - $5/month credits  
✅ **Built-in PostgreSQL** - Easy to add databases later  
✅ **Environment variables** - GUI and CLI tools  
✅ **Docker support** - Uses Dockerfile if available  
✅ **Pull request previews** - Automatic staging environments  

## Deployment Steps

Currently deploying **backend only**. The frontend is prepared for future use but not deployed yet.

### Backend Deployment

#### Option A: Using Railway Dashboard (Easiest)

1. Go to https://railway.app/dashboard
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `hakeemsyd/books-service`
4. Railway will detect the Dockerfile automatically
5. Add environment variables:
   - `AIRTABLE_TOKEN=your_token`
   - `AIRTABLE_BASE_ID=your_base_id`
   - `SLACK_BOT_TOKEN=your_bot_token`
   - `SLACK_SIGNING_SECRET=your_signing_secret`
   - `EXCLUDED_ACCOUNT_IDS=rec123,rec456`
6. Click **Deploy**

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd backend
railway init

# Add environment variables
railway variables set AIRTABLE_TOKEN=your_token
railway variables set AIRTABLE_BASE_ID=your_base_id
railway variables set SLACK_BOT_TOKEN=your_bot_token
railway variables set SLACK_SIGNING_SECRET=your_signing_secret

# Deploy
railway up
```

#### Backend URL

Once deployed, Railway provides a public URL:
```
https://books-service-prod.railway.app
```

Update your Slack slash command Request URL:
```
https://books-service-prod.railway.app/slack/run-books
```

### Frontend (Future)

The frontend is prepared for future deployment but not currently needed. All interaction happens via Slack slash commands.

When ready to deploy the frontend:
- It's already configured with TypeScript and production build setup
- Just add a new Railway service pointing to the `frontend/` directory
- Frontend will communicate with the deployed backend API

## Environment Variables

### Backend Required Variables

Add these in Railway dashboard or via CLI:

```env
# Airtable
AIRTABLE_TOKEN=pat...
AIRTABLE_BASE_ID=app...
AIRTABLE_TABLE_NAME=Transactions
AIRTABLE_CATEGORIES_TABLE=Categories

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_CHANNEL_ID=C...

# Optional
EXCLUDED_ACCOUNT_IDS=rec123,rec456
MIN_SEEN=3
MIN_CONSISTENCY=0.9
MAX_HISTORY_PAGES=50
```

### Frontend Environment Variables

```env
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## Automatic Deployments

Both services are configured to auto-deploy on every push to `main`:

1. Push to GitHub: `git push origin main`
2. Railway automatically detects changes
3. Builds and deploys both backend and frontend
4. Takes ~2-5 minutes for each service

### Disable Auto-Deploy (Optional)

In Railway dashboard:
1. Select service → Settings
2. Turn off "Automatically deploy on push"

## View Logs

### Via Dashboard
- Railway dashboard → Service → Deployments → View logs

### Via CLI
```bash
railway logs  # Stream logs in real-time
railway logs -n 100  # View last 100 lines
```

## Database (Optional Future)

When ready to add a database:

1. In Railway project, click **New**
2. Select **PostgreSQL** or **MySQL**
3. Railway creates credentials automatically
4. Add connection string to backend environment variables
5. Update `backend/src/db/` with database models

## Domains & SSL

Railway provides:
- ✅ Free `.railway.app` domain with auto SSL
- ✅ Custom domain support (paid feature)

To use a custom domain:
1. Railway dashboard → Service → Settings
2. Add custom domain (e.g., `api.yourdomain.com`)
3. Update DNS CNAME records
4. Auto SSL certificate issued

## Monitoring

Railway provides basic monitoring:
- Deployment history and logs
- Environment variable management
- Auto-redeploy on failure
- Health checks via Dockerfile HEALTHCHECK

## Scaling

### Backend Scaling
1. Dashboard → Service → Settings
2. Adjust resources or enable auto-scaling
3. Railway handles container management

### Frontend Scaling
Static files scale automatically, no configuration needed.

## Troubleshooting

### Deployment Failed
```bash
# Check build logs in Dashboard
# Or via CLI:
railway logs
```

### Environment Variables Not Working
```bash
# Verify variables are set
railway variables

# Re-deploy after adding variables
railway up
```

### API Connection Issues
1. Verify backend URL is correct
2. Check Slack signing secret is exact match
3. Review backend logs: `railway logs`

### Frontend Can't Reach Backend
1. Check `REACT_APP_API_URL` environment variable
2. Ensure backend is deployed and running
3. Check CORS settings in backend if needed

## Costs

Railway free tier includes:
- **$5/month** free credits
- Unlimited projects and services
- Each service runs on shared infrastructure

Typical usage:
- Backend: ~$2-3/month
- Frontend: ~$1-2/month
- Total: Well under $5/month free tier

## CI/CD with GitHub Actions

Optional: Add GitHub Actions for additional checks:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: npm i -g @railway/cli && railway up
```

## Rollback

To rollback to previous deployment:
1. Railway dashboard → Service → Deployments
2. Click on previous deployment
3. Click **Redeploy**

This redeploys the exact previous version.

## Resources

- [Railway Docs](https://docs.railway.app)
- [Railway CLI Guide](https://docs.railway.app/guides/cli)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Railway Custom Domains](https://docs.railway.app/develop/domains)

## Support

- Railway Support: https://railway.app/support
- GitHub Issues: https://github.com/hakeemsyd/books-service/issues
