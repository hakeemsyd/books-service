# Books Categorization Service

A **monorepo** containing a FastAPI backend and React frontend for managing book categorization with a Supabase (Postgres) database and Slack integration.

## Overview

The Books Service lets you trigger automatic transaction categorization directly from Slack using the `/run-books` command. It reads transactions from a Supabase Postgres database and categorizes uncategorized ones using:

1. **Tier 1 (Statistical)**: Matches against historical data — auto-categorizes if seen ≥ 3 times at exact account+merchant with ≥ 90% consistency
2. **Tier 2 (Keyword Rules)**: Pattern matching against category names — suggests categories with lower confidence for your review

The service includes both:
- **Backend**: Python FastAPI REST API with clean architecture
- **Frontend**: React + TypeScript + Vite dashboard for monitoring and management

## Project Structure

```
books-service/
├── backend/          # FastAPI API + Supabase schema
├── frontend/         # React dashboard
└── PROJECT_STRUCTURE.md  # Detailed architecture docs
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete directory layout and scaling patterns.

## What It Does NOT Do

- Never pulls/syncs transactions from banks — that's a separate sync process (Plaid, Fintable, CSV import, etc.) that writes into the `transactions` table
- Never modifies already-categorized transactions
- Never touches excluded accounts — set `accounts.excluded = true` for those accounts

## Quick Start

### Prerequisites

- Python 3.9+ (backend)
- Node.js 16+ (frontend)
- A Supabase project (free tier is fine)
- Git

### 1. Clone and Setup

```bash
git clone <repo-url>
cd books-service

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Frontend setup
cd ../frontend
npm install
cp .env.example .env
```

### 2. Set Up the Database

See [backend/supabase/README.md](./backend/supabase/README.md) for full instructions. Short version:

1. Create a project at https://supabase.com/dashboard
2. Run `backend/supabase/schema.sql` in the Supabase SQL Editor
3. Edit and run `backend/supabase/seed.sql` with your real business/category names
4. Copy the connection string (Project Settings → Database → Connection string → URI) into `backend/.env` as `DATABASE_URL`

### 3. Get Slack Credentials

**Slack App** (api.slack.com/apps → Create New App):
1. **OAuth & Permissions** → Bot Token Scopes: add `commands`, `chat:write`
2. Install to workspace → copy Bot User OAuth Token (`xoxb-...`)
3. Copy **Signing Secret** from Basic Information
4. **Slash Commands** → Create New:
   - Command: `/run-books`
   - Request URL: `http://localhost:8000/slack/run-books` (development) or your deployed URL
   - Short description: "Run books categorization now"

Add tokens to `backend/.env`.

## Running Locally

### Development (Both Apps)

```bash
# Terminal 1: Backend API (http://localhost:8000)
cd backend
uvicorn src.main:app --reload

# Terminal 2: Frontend (http://localhost:3000)
cd frontend
npm run dev
```

The frontend will proxy API requests to the backend at `http://localhost:8000`.

### Production Build

```bash
# Backend: Already running as above
# Frontend: Build for production
cd frontend
npm run build
# Output: frontend/dist/
```

## Usage

### Slack Command

In any Slack channel, type `/run-books` to trigger categorization.

Expected flow:
1. Immediate ephemeral ack: "⏳ Running books categorization now..."
2. Few seconds to 2+ minutes later (depending on transaction volume):
   - ✅ Auto-categorized (high confidence, `reviewed = true`)
   - 🟡 Suggested — review in the database (`reviewed = false`)
   - 🔴 Needs manual categorization (left untouched)

### Frontend Dashboard

Visit http://localhost:3000 (development) to view the dashboard. Features to come:
- View categorization history
- Batch operations
- Configuration management

## Configuration

All settings are environment-driven. See `backend/.env.example` and `frontend/.env.example`.

**Backend** (`backend/.env`):
- `DATABASE_URL` — Supabase Postgres connection string
- `SLACK_BOT_TOKEN` — Bot token
- `SLACK_SIGNING_SECRET` — Signing secret
- `MIN_SEEN` — Tier-1 minimum occurrences (default: 3)
- `MIN_CONSISTENCY` — Tier-1 consistency threshold (default: 0.9)

**Frontend** (`frontend/.env`):
- `REACT_APP_API_URL` — Backend API endpoint (default: `/api`)

## Deployment

Currently deploying **backend only** to handle Slack `/run-books` commands. The frontend is prepared for future use.

### Railway.app (Recommended)

Railway is the easiest way to deploy the backend:

1. Go to https://railway.app
2. Create account and connect GitHub
3. Add new project, select this repository
4. Railway auto-detects the backend Dockerfile
5. Add environment variables (`DATABASE_URL`, Slack credentials)
6. Deploy - backend redeploys automatically on every push to `main`
7. Update your Slack slash command Request URL to the Railway URL

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

**Cost:** Free tier includes $5/month credits  
**URL:** Backend gets automatic `.railway.app` domain with SSL  
**Response time:** 2-5 minutes per deployment

### Alternative: Self-Hosted Backend

```bash
# Build Docker image
cd backend
docker build -t books-api .

# Run locally
docker run -p 8000:8000 \
  -e DATABASE_URL=your_supabase_connection_string \
  -e SLACK_BOT_TOKEN=your_bot_token \
  -e SLACK_SIGNING_SECRET=your_secret \
  books-api
```

Deploy to any Docker host (AWS, Digital Ocean, Heroku, etc.)

### Frontend (Future)

The frontend is built and ready for deployment whenever needed. It communicates with the backend API and displays categorization results. Not currently deployed.

## Architecture

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for:
- Detailed layer separation
- How to add new features
- Testing patterns
- Scaling considerations
- Import patterns

## Tuning & Customization

- **Tier-1 thresholds**: Adjust `MIN_SEEN` and `MIN_CONSISTENCY` in `backend/.env`
- **Tier-2 rules**: Edit `SEMANTIC_RULES` in `backend/src/services/categorizer.py`
- **Excluded accounts**: Set `excluded = true` on the account row in the `accounts` table
- **Categories per business**: Managed via the `category_businesses` junction table — see `backend/supabase/README.md`

This service runs independently of any scheduled tasks — it's purely on-demand via `/run-books`.
