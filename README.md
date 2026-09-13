# Books Categorization Service

A **monorepo** containing a FastAPI backend and React frontend for managing book categorization with Airtable and Slack integration.

## Overview

The Books Service lets you trigger automatic transaction categorization directly from Slack using the `/run-books` command. It analyzes your Airtable "Book Keeping" base and categorizes uncategorized transactions using:

1. **Tier 1 (Statistical)**: Matches against historical data — auto-categorizes if seen ≥ 3 times at exact account+merchant with ≥ 90% consistency
2. **Tier 2 (Keyword Rules)**: Pattern matching against category names — suggests categories with lower confidence for your review

The service includes both:
- **Backend**: Python FastAPI REST API with clean architecture
- **Frontend**: React + TypeScript + Vite dashboard for monitoring and management

## Project Structure

```
books-service/
├── backend/          # FastAPI API
├── frontend/         # React dashboard
└── PROJECT_STRUCTURE.md  # Detailed architecture docs
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete directory layout and scaling patterns.

## What It Does NOT Do

- Never pulls/syncs transactions from banks — your existing sync (Plaid, Fintable) continues as normal
- Never modifies already-categorized transactions
- Never touches excluded accounts — configure in `backend/.env`

## Quick Start

### Prerequisites

- Python 3.9+ (backend)
- Node.js 16+ (frontend)
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

### 2. Get Your Credentials

**Airtable Personal Access Token** (airtable.com/create/tokens):
- Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
- Access: your "Book Keeping" base

**Slack app** (api.slack.com/apps → Create New App → From scratch):
1. **OAuth & Permissions** → Bot Token Scopes: add `commands`, `chat:write`.
   Install to workspace → copy the `xoxb-...` **Bot User OAuth Token**.
2. **Basic Information** → copy the **Signing Secret**.
3. **Slash Commands** → Create New Command:
   - Command: `/run-books`
   - Request URL: `https://<your-render-service>.onrender.com/slack/run-books`
   - Short description: "Run books categorization now"
4. Invite the bot to `#airtable-finances`: `/invite @YourAppName`.

### 3. Backend Credentials

**Airtable Personal Access Token** (airtable.com/create/tokens):
- Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
- Access: your "Book Keeping" base

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
   - ✅ Auto-categorized (high confidence, Reviewed = true)
   - 🟡 Suggested — review in Airtable (Reviewed = false)
   - 🔴 Needs manual categorization (left untouched)

### Frontend Dashboard

Visit http://localhost:3000 (development) to view the dashboard. Features to come:
- View categorization history
- Batch operations
- Configuration management

## Configuration

All settings are environment-driven. See `backend/.env.example` and `frontend/.env.example`.

**Backend** (`backend/.env`):
- `AIRTABLE_TOKEN` — API token
- `AIRTABLE_BASE_ID` — Base ID
- `SLACK_BOT_TOKEN` — Bot token
- `SLACK_SIGNING_SECRET` — Signing secret
- `MIN_SEEN` — Tier-1 minimum occurrences (default: 3)
- `MIN_CONSISTENCY` — Tier-1 consistency threshold (default: 0.9)
- Optional: field name overrides, excluded account IDs

**Frontend** (`frontend/.env`):
- `REACT_APP_API_URL` — Backend API endpoint (default: `/api`)

## Deployment

### Backend (Render.com)

1. Push to GitHub
2. Connect repo to Render → detects `backend/render.yaml`
3. Add environment variables in Render dashboard
4. Deploy → update Slack slash command Request URL

Note: Render free tier may take 30-50s to wake up on first request after idle.

### Frontend (Static Hosting)

```bash
cd frontend
npm run build
# Deploy frontend/dist/ to Netlify, Vercel, S3, etc.
```

Update `REACT_APP_API_URL` in frontend environment for production API endpoint.

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
- **Excluded accounts**: Set `EXCLUDED_ACCOUNT_IDS` in `backend/.env`
- **Field names**: Override defaults in `backend/.env` if your Airtable structure differs

This service runs independently of any scheduled tasks — it's purely on-demand via `/run-books`.
