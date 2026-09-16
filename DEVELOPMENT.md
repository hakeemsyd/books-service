# Development Guide

Quick reference for common development tasks.

## Initial Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your actual credentials

# Frontend
cd ../frontend
npm install
cp .env.example .env
```

## Running Locally

```bash
# Terminal 1: Backend (API on :8000)
cd backend
uvicorn src.main:app --reload

# Terminal 2: Frontend (UI on :3000)
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Common Commands

### Backend

```bash
cd backend

# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Check code style
flake8 src
black --check src

# Format code
black src

# Run linter
pylint src
```

### Frontend (TypeScript + React + Vite)

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run type-check

# Linting (check for issues)
npm run lint

# Linting (auto-fix issues)
npm run lint:fix

# Code formatting
npm run format

# Check if formatted
npm run format:check

# Build for production (includes type checking)
npm run build

# Preview production build
npm run preview
```

## Adding Dependencies

### Backend

```bash
cd backend
pip install <package>
pip freeze > requirements.txt
```

### Frontend

```bash
cd frontend
npm install <package>
# or
npm install --save-dev <package-dev>
```

## Directory Quick Reference

```
backend/
  src/
    main.py              ← FastAPI app entry point
    config.py            ← Configuration
    api/routes.py        ← API endpoints
    services/            ← Business logic
    clients/             ← External integrations
  tests/                 ← Test suite
  requirements.txt
  .env                   ← Local config (git-ignored)
  render.yaml            ← Render deployment

frontend/
  src/
    main.jsx             ← React entry
    App.jsx              ← Root component
    components/          ← Reusable components
    pages/               ← Page components
    services/api.js      ← API client
  package.json
  vite.config.js
  .env                   ← Local config (git-ignored)
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push and create PR
git push origin feature/your-feature

# After merging to main, deploy both apps
# Backend: Push to main triggers Render deployment
# Frontend: Run 'npm run build' and deploy dist/ to hosting
```

## Debugging

### Backend

Enable debug logging:
```python
# In backend/src/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend

React DevTools browser extension recommended.

Check API calls:
```javascript
// frontend/src/services/api.js
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response);
    return response;
  },
  error => {
    console.error('API Error:', error);
    throw error;
  }
);
```

## Slack Testing

### Local Testing

1. Install ngrok: `brew install ngrok`
2. Start ngrok tunnel: `ngrok http 8000`
3. Update Slack slash command Request URL to ngrok URL
4. Backend must be running: `uvicorn src.main:app --reload`
5. Test command in Slack: `/run-books`

### Testing in Production

Deploy backend to Render, update Request URL, test from Slack.

## Database (When Needed)

If adding database support:
1. Create `backend/src/db/` directory
2. Add ORM (SQLAlchemy) or query builder
3. Store connection in config
4. Add migrations system
5. Update models in `backend/src/services/`

## Environment Variables

### Adding a New Variable

**Backend:**
1. Add to `backend/.env.example`
2. Load in `backend/src/config.py` using `os.environ.get()`
3. Document in this file

**Frontend:**
1. Add to `frontend/.env.example` with `REACT_APP_` prefix
2. Access in code: `process.env.REACT_APP_VARIABLE`
3. Document in this file

## Performance Tips

### Backend
- Use async/await for all I/O
- The asyncpg connection pool is created once at startup (see `src/main.py` lifespan) — don't open new connections per-request
- Batch writes with `executemany` (already used in `update_transactions`)
- Monitor with `/metrics` endpoint (add prometheus later)

### Frontend
- Code split route components with React.lazy()
- Optimize images and assets
- Use React memo for expensive components
- Monitor bundle size: `npm run build -- --stats`

## Troubleshooting

### Backend won't start
```bash
cd backend
pip install -r requirements.txt  # Reinstall deps
python -c "from src.main import app"  # Check syntax
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API calls failing
1. Check backend is running: `curl http://localhost:8000/`
2. Check proxy in `frontend/vite.config.js`
3. Check browser console for CORS errors
4. Check backend logs for errors

### Slack not responding
1. Verify Request URL is accessible
2. Check signing secret in `backend/.env`
3. Check backend logs for signature errors
4. Verify Slack bot permissions

## Docker & Deployment

### Build & Run with Docker

```bash
# Backend
cd backend
docker build -t books-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=your_supabase_connection_string \
  -e SLACK_BOT_TOKEN=your_bot_token \
  -e SLACK_SIGNING_SECRET=your_secret \
  books-api

# Frontend
cd frontend
docker build -t books-web .
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  books-web
```

### Deploy Backend to Railway

Currently only the backend is deployed. Slack commands trigger the `/slack/run-books` endpoint.

See [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) for full instructions.

Quick start:
```bash
# Option 1: Railway Dashboard (easiest)
# - Go to railway.app
# - Connect GitHub repo
# - Add environment variables
# - Deploy

# Option 2: Railway CLI
npm install -g @railway/cli
cd backend
railway init
railway variables set DATABASE_URL=...
railway variables set SLACK_BOT_TOKEN=...
railway variables set SLACK_SIGNING_SECRET=...
railway up
```

Update your Slack slash command Request URL to the deployed backend URL.

## Resources

- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Vite: https://vitejs.dev
- Supabase: https://supabase.com/docs
- asyncpg: https://magicstack.github.io/asyncpg/
- Slack API: https://api.slack.com
- Railway: https://railway.app

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details.
See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for deployment guide.
