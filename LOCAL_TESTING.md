# Local Testing Guide

## Setup & Run Backend Locally

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your actual credentials:

```bash
cp .env.example .env
```

Edit `backend/.env` with your real values:

```env
# Database (Supabase Postgres)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# Slack
SLACK_BOT_TOKEN=xoxb-XXXXXXXXXXXX
SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
SLACK_CHANNEL_ID=C0C2AEDFSGY
```

**Where to get these:**
- **DATABASE_URL**: Supabase dashboard → Project Settings → Database → Connection string → URI (see `backend/supabase/README.md` for full setup, including schema + seed)
- **SLACK_BOT_TOKEN**: Slack app settings → OAuth & Permissions
- **SLACK_SIGNING_SECRET**: Slack app settings → Basic Information

### 3. Start Backend Server

```bash
source venv/bin/activate  # Make sure venv is active

# Run development server (auto-reload on file changes)
uvicorn src.main:app --reload

# Or run with custom port
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4. Test Health Endpoint

In another terminal:

```bash
# Test health check
curl http://localhost:8000/

# Should respond with:
{"status":"ok"}
```

### 5. View API Documentation

Open your browser:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 6. Test Slack Integration Locally

#### Option A: Using ngrok (for Slack Request URL)

```bash
# Install ngrok if you haven't
brew install ngrok

# Start ngrok tunnel to port 8000
ngrok http 8000
```

This gives you a public URL like `https://abc123.ngrok.io`

Update your Slack slash command:
- Request URL: `https://abc123.ngrok.io/slack/run-books`

Now you can test `/run-books` in Slack!

#### Option B: Direct Testing (without Slack)

Test the endpoint directly using curl:

```bash
# Create a test Slack request
curl -X POST http://localhost:8000/slack/run-books \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "response_url=https://hooks.slack.com/commands/..." \
  -d "channel_id=C0C2AEDFSGY"
```

### 7. Verify Imports

Test that all modules import correctly:

```bash
python -c "from src.main import app; print('✅ App imported successfully')"
python -c "from src.services import categorize_batch; print('✅ Services imported successfully')"
python -c "from src.clients import fetch_categories; print('✅ Clients imported successfully')"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Check Python version
python --version
# Reinstall requirements
pip install -r requirements.txt
```

### "KeyError: 'DATABASE_URL'"
- Create `.env` file in `backend/` directory
- Add all required environment variables
- Restart the server

### "connection refused" / asyncpg can't reach Postgres
- Double-check `DATABASE_URL` — use the Session pooler string from Supabase, not the direct connection, if you're behind a restrictive network
- Confirm the schema has been applied (see `backend/supabase/README.md`)

### "Connection refused" when testing Slack
- Make sure backend is running on port 8000
- If using ngrok, make sure ngrok tunnel is active
- Slack Request URL must be publicly accessible

### Slack signature verification fails
- Check `SLACK_SIGNING_SECRET` is exactly correct
- Make sure it's the "Signing Secret", not the "Bot Token"
- Restart backend after changing .env

## Development Workflow

```bash
# Terminal 1: Run backend with hot reload
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2 (optional): Monitor logs
cd backend
source venv/bin/activate
tail -f logs/app.log

# Terminal 3: Run tests
cd backend
source venv/bin/activate
pytest -v
```

## Environment Variables Explanation

| Variable | Purpose | Required |
|----------|---------|----------|
| DATABASE_URL | Supabase Postgres connection string | Yes |
| SLACK_BOT_TOKEN | Slack bot authentication | Yes |
| SLACK_SIGNING_SECRET | Verify Slack requests | Yes |
| SLACK_CHANNEL_ID | Default channel (fallback) | No |
| MIN_SEEN | Tier-1 min occurrences | No (default: 3) |
| MIN_CONSISTENCY | Tier-1 min consistency | No (default: 0.9) |

Account exclusions are no longer an env var — set `excluded = true` directly on the account row in the `accounts` table.

## Next Steps

After successful local testing:
1. Test the Slack command: `/run-books` in your workspace
2. Verify transactions are categorized correctly
3. Check Slack channel for results
4. Deploy to Railway when ready: See [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md)
