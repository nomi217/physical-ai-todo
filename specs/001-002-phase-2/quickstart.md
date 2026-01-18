# Quickstart Guide - Phase II

**Feature**: Phase II - Full-Stack Web Application
**Tech Stack**: Next.js 14 + FastAPI + SQLModel + Neon DB
**Estimated Setup Time**: 30-45 minutes

---

## Prerequisites

### Required Software

1. **Python 3.13+**
   ```bash
   python --version  # Should be 3.13.0 or higher
   ```
   Download: https://www.python.org/downloads/

2. **Node.js 18+ and npm**
   ```bash
   node --version  # Should be v18.0.0 or higher
   npm --version   # Should be 9.0.0 or higher
   ```
   Download: https://nodejs.org/

3. **Git**
   ```bash
   git --version
   ```
   Download: https://git-scm.com/

### Required Accounts

4. **Neon DB Account** (Free)
   - Sign up: https://neon.tech
   - Create a new project
   - Save your connection string

5. **Anthropic API Key** (For AI chatbot)
   - Sign up: https://console.anthropic.com
   - Generate API key
   - Note: Free tier available, $5 credit for testing

---

## Project Structure

```
physical-ai-todo/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── src/todo/         # Phase I code (preserved)
├── specs/            # Documentation
└── README.md
```

---

## 1. Clone Repository

```bash
git clone https://github.com/nomi217/physical-ai-todo.git
cd physical-ai-todo
```

---

## 2. Backend Setup (FastAPI)

### 2.1 Create Virtual Environment

**Linux/Mac**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.104.1
sqlmodel==0.0.14
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
asyncpg==0.29.0
anthropic==0.7.8
pydantic==2.5.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### 2.3 Configure Environment

Create `.env` file in `backend/` directory:

```bash
# Database (Neon DB)
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.neon.tech/dbname?sslmode=require

# AI Integration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxx

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Server
PORT=8000
ENVIRONMENT=development
```

**Get Neon DB Connection String**:
1. Go to https://console.neon.tech
2. Select your project
3. Click "Connection string"
4. Copy the asyncpg format
5. Replace `postgresql://` with `postgresql+asyncpg://`

### 2.4 Initialize Database

```bash
# Still in backend/ directory
python -m app.database
```

This will:
- Connect to Neon DB
- Create all tables (tasks, voice_commands, chat_messages)
- Verify connection

### 2.5 Run Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## 3. Frontend Setup (Next.js)

### 3.1 Install Dependencies

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm install
```

**package.json dependencies**:
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.0",
    "@anthropic-ai/sdk": "^0.9.1",
    "swr": "^2.2.4",
    "i18next": "^23.7.0",
    "react-i18next": "^13.5.0",
    "next-i18next": "^15.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.4"
  }
}
```

### 3.2 Configure Environment

Create `.env.local` file in `frontend/` directory:

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Anthropic API (for client-side chat)
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxx
```

### 3.3 Run Frontend Development Server

```bash
npm run dev
```

**Verify**:
- Frontend: http://localhost:3000
- Should see todo dashboard

---

## 4. Verify Installation

### 4.1 Test Backend

```bash
# In new terminal
curl http://localhost:8000/api/v1/tasks
```

Expected response:
```json
{
  "tasks": [],
  "total": 0,
  "limit": 50,
  "offset": 0
}
```

### 4.2 Test Frontend

1. Open http://localhost:3000
2. Click "Add Task" button
3. Enter title "Test Task"
4. Click "Save"
5. Task should appear in list

### 4.3 Test Multi-language

1. Click language selector (top right)
2. Select "Español"
3. UI should change to Spanish

### 4.4 Test Voice (Chrome/Edge only)

1. Click microphone button
2. Grant microphone permission
3. Say "Add task buy milk"
4. Task should be created

---

## 5. Running Tests

### 5.1 Backend Tests

```bash
cd backend
pytest
```

**Expected**:
```
======================== test session starts ========================
tests/test_crud.py ........                                   [ 50%]
tests/test_api.py ........                                    [100%]

======================== 16 passed in 2.34s =========================
```

### 5.2 Frontend Tests

```bash
cd frontend
npm test
```

---

## 6. Development Workflow

### 6.1 Starting Development

**Terminal 1** (Backend):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2** (Frontend):
```bash
cd frontend
npm run dev
```

### 6.2 Stopping Servers

- Press `Ctrl+C` in each terminal
- Deactivate Python venv: `deactivate`

### 6.3 Code Structure

**Backend** (`backend/app/`):
```
app/
├── main.py              # FastAPI app + routes registration
├── database.py          # Neon DB connection
├── models.py            # SQLModel table definitions
├── schemas.py           # Pydantic request/response schemas
├── crud.py              # Database operations
├── routes/
│   ├── tasks.py         # Task CRUD endpoints
│   ├── voice.py         # Voice command endpoints
│   └── chat.py          # AI chatbot endpoints
└── services/
    ├── voice_service.py # Voice processing
    └── ai_service.py    # Claude integration
```

**Frontend** (`frontend/`):
```
app/
├── page.tsx             # Main dashboard
├── layout.tsx           # Root layout
└── globals.css          # Global styles

components/
├── TaskList.tsx         # Task list
├── TaskForm.tsx         # Add/edit form
├── TaskItem.tsx         # Individual task
├── FilterBar.tsx        # Search/filter
├── VoiceInput.tsx       # Voice button
├── ChatBot.tsx          # AI chat panel
└── LanguageSelector.tsx # Language switcher

lib/
├── api.ts               # API client functions
├── types.ts             # TypeScript types
└── voice.ts             # Voice utilities
```

---

## 7. Common Issues & Solutions

### Issue 1: Database Connection Error

**Error**: `asyncpg.exceptions.InvalidPasswordError`

**Solution**:
1. Verify Neon DB connection string in `.env`
2. Ensure `?sslmode=require` is at the end
3. Check username/password are correct
4. Verify Neon DB project is active (not paused)

---

### Issue 2: CORS Error in Frontend

**Error**: `Access to fetch at 'http://localhost:8000' ... has been blocked by CORS policy`

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure `http://localhost:3000` is included
3. Restart backend server

---

### Issue 3: Voice Recognition Not Working

**Error**: "Speech recognition not supported"

**Solution**:
1. Use Chrome or Edge (Firefox has limited support)
2. Grant microphone permission when prompted
3. Check browser console for errors
4. Verify microphone is working in system settings

---

### Issue 4: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue 5: Port Already in Use

**Error**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solution**:
```bash
# Find process using port 3000
lsof -ti:3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

---

## 8. Database Management

### View All Tasks in Database

```bash
# Using psql (install from https://www.postgresql.org/download/)
psql "postgresql://username:password@ep-xxx.neon.tech/dbname?sslmode=require"

# In psql shell:
SELECT * FROM task;
```

### Reset Database

```bash
# In psql:
DROP TABLE task CASCADE;
DROP TABLE voicecommand CASCADE;
DROP TABLE chatmessage CASCADE;

# Then re-run:
python -m app.database
```

---

## 9. Docker Setup (Optional)

### Using Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

**Run**:
```bash
docker-compose up --build
```

---

## 10. Deployment

### Deploy Backend (Railway)

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

3. Set environment variables in Railway dashboard

### Deploy Frontend (Vercel)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   cd frontend
   vercel
   ```

3. Set environment variables in Vercel dashboard

---

## 11. API Documentation

**Interactive Docs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 12. Multi-language Setup

### Adding a New Language

1. Create translation file: `frontend/public/locales/<lang>/common.json`

2. Add language to `next-i18next.config.js`:
   ```javascript
   locales: ['en', 'ur', 'ar', 'es', 'fr', 'de', 'hi']  // Added Hindi
   ```

3. Add flag icon to `frontend/public/flags/<lang>.svg`

4. Update language codes in `lib/voice.ts`:
   ```typescript
   const codes = {
     ...
     'hi': 'hi-IN'
   }
   ```

---

## 13. Next Steps

After successful setup:

1. **Explore Features**:
   - Create tasks with different priorities
   - Add tags and filter by them
   - Test search functionality
   - Try voice commands in different languages
   - Chat with AI assistant

2. **Run Tests**:
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm test
   ```

3. **Read Documentation**:
   - API Examples: `specs/001-002-phase-2/contracts/api-examples.md`
   - Data Model: `specs/001-002-phase-2/data-model.md`
   - Full Spec: `specs/001-002-phase-2/spec.md`

4. **Start Development**:
   - Review implementation plan: `specs/001-002-phase-2/plan.md`
   - Generate tasks: Run `/sp.tasks` command
   - Begin implementation: Run `/sp.implement` command

---

## 14. Support

**Issues**: https://github.com/nomi217/physical-ai-todo/issues
**Documentation**: `specs/001-002-phase-2/`

---

**Quickstart Status**: ✅ Complete
**Estimated Setup Time**: 30-45 minutes
**Difficulty**: Intermediate
