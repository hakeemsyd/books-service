# Project Structure

This is a **monorepo** with both backend (Python/FastAPI) and frontend (React) applications in a single repository. Each app is independently deployable while sharing a common workspace.

## Directory Layout

```
books-service/
├── backend/                       # Backend API (Python/FastAPI)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── config.py             # Configuration management
│   │   ├── clients/              # External service integrations
│   │   │   ├── __init__.py
│   │   │   ├── airtable_client.py
│   │   │   └── slack_client.py
│   │   ├── services/             # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── categorizer.py
│   │   └── api/                  # API routes
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── tests/                    # Backend pytest tests
│   │   ├── test_categorizer.py
│   │   ├── test_routes.py
│   │   └── conftest.py
│   ├── .env                      # Local environment (backend)
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Python dependencies
│   └── render.yaml               # Render deployment config
│
├── frontend/                     # Frontend (React/TypeScript/Vite)
│   ├── public/
│   │   └── index.html           # HTML entry point
│   ├── src/
│   │   ├── main.tsx             # React entry point (typed)
│   │   ├── App.tsx              # Root component (typed)
│   │   ├── vite-env.d.ts        # Environment types
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API & utility services
│   │   │   └── api.ts          # Typed API client
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/               # TypeScript type definitions
│   │   └── styles/              # CSS files
│   ├── __tests__/ or *.test.tsx # Frontend tests (optional)
│   ├── .gitignore              # Frontend-specific ignores
│   ├── package.json            # NPM dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vite.config.ts          # Vite configuration (typed)
│   ├── .eslintrc.json          # ESLint rules
│   ├── .prettierrc.json        # Code formatting
│   └── .env.example            # Frontend environment template
│
├── .gitignore                   # Root-level git ignores
├── README.md                    # Project documentation
└── PROJECT_STRUCTURE.md         # This file
```

## Backend Architecture

### Layer Separation (`backend/src/`)

1. **API Layer** (`api/routes.py`)
   - FastAPI routes and request handlers
   - Handles HTTP requests/responses
   - Orchestrates business logic

2. **Services Layer** (`services/`)
   - Core business logic
   - Data transformation and processing
   - Pure functions when possible for testability

3. **Clients Layer** (`clients/`)
   - External integrations: Supabase Postgres (`db_client.py`) and Slack (`slack_client.py`)
   - Encapsulates external dependencies
   - Reusable across services

4. **Configuration** (`config.py`)
   - Centralized environment variable management
   - Single source of truth for settings

## Frontend Architecture

### Structure (`frontend/src/`)

- **main.jsx** - React entry point
- **App.jsx** - Root component
- **components/** - Reusable UI components
- **pages/** - Page-level components
- **services/** - API clients, utilities
- **hooks/** - Custom React hooks
- **styles/** - CSS and styling

## Running the Application

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```
Backend runs on `http://localhost:8000`

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:3000` with proxy to backend at `/api`

### Both Together (Concurrent)
From root directory:
```bash
# Terminal 1: Backend
cd backend && uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Production Build

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
# Output in frontend/dist/
```

## Adding New Features

### Backend: Adding a New Service
1. Create a new module in `backend/src/services/`
2. Import and export functions in `backend/src/services/__init__.py`
3. Use in routes via `backend/src/api/routes.py`

### Backend: Adding a New API Route
1. Update or create route handlers in `backend/src/api/routes.py`
2. Follow the existing pattern with proper error handling
3. Add tests in `backend/tests/test_routes.py`

### Backend: Adding a New External Client
1. Create a new module in `backend/src/clients/`
2. Implement client functions
3. Import and export in `backend/src/clients/__init__.py`
4. Use in services or routes as needed

### Frontend: Adding a New Component
1. Create component file in `frontend/src/components/`
2. Import in pages or other components
3. Use existing `services/api.js` for backend communication

### Frontend: Adding a New Page
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Update navigation as needed

## Testing

Tests are organized within each app's directory, not at the root level.

### Backend Tests
Backend tests use **pytest** and live in `backend/tests/`:

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_categorizer.py

# Verbose output
pytest -v

# With coverage report
pytest --cov=src

# Run tests with type checking
pytest && npm run type-check
```

### Frontend Tests
Frontend tests use **Vitest** or **Jest** (optional, add as needed):

```bash
cd frontend

# Add testing library (optional)
npm install --save-dev vitest @testing-library/react

# Run tests
npm test

# With coverage
npm test -- --coverage
```

Tests should be colocated with features or in a `__tests__` directory within `frontend/src/`.

## Import Patterns

### Backend (relative imports within backend/src/)
```python
from ..config import SETTING_NAME           # Up to src, then to config
from ..services import function_name         # Up to src, then to services
from ..clients import function_name          # Up to src, then to clients
```

### Frontend (within frontend/src/)
```javascript
import { component } from '../components/name'
import { apiFunction } from '../services/api'
import { useHook } from '../hooks/name'
```

## Environment Variables

### Backend (`backend/.env`)
See `backend/.env.example`:
- `DATABASE_URL` - Supabase Postgres connection string
- `SLACK_BOT_TOKEN` - Slack bot token
- `SLACK_SIGNING_SECRET` - Slack signing secret
- Optional matching thresholds (`MIN_SEEN`, `MIN_CONSISTENCY`)

See `backend/supabase/README.md` for the database schema and setup.

### Frontend (`frontend/.env`)
- `REACT_APP_API_URL` - Backend API URL (defaults to `/api`)

## Scaling Considerations

### Backend
- **Multiple clients**: Add to `src/clients/`
- **Multiple services**: Add to `src/services/`
- **Multiple API versions**: Create `src/api/v1/`, `src/api/v2/` subdirectories
- **Background tasks**: Can be extracted to `src/tasks/`
- **Database layer**: Can be added as `src/db/` when needed
- **Middleware**: Can be added to FastAPI app in `src/main.py`

### Frontend
- **Page organization**: Group related pages in subdirectories
- **Component libraries**: Organize components by feature
- **State management**: Add Redux, Zustand, or Context as app grows
- **API expansion**: Add more services in `services/` directory
- **Styling system**: Organize CSS/SCSS by component or feature

## Deployment

### Backend Deployment
Backend has `render.yaml` configured for Render.com deployment.
Update with your environment variables and deploy URL.

### Frontend Deployment
Build frontend and serve from static hosting or backend:
```bash
cd frontend
npm run build
# Deploy frontend/dist to CDN or static server
```

## Monorepo Commands

Useful patterns for working with both apps:

```bash
# Run both in parallel (from root)
# Terminal 1
cd backend && uvicorn src.main:app --reload

# Terminal 2
cd frontend && npm run dev

# Install dependencies for both
cd backend && pip install -r requirements.txt && cd ../frontend && npm install

# Test both
cd backend && pytest && cd ../frontend && npm test
```
