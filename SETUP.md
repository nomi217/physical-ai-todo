# Physical AI Todo - Setup Guide

## ✅ Phase 1 & 2 Complete

The project structure and foundation have been created. Follow these steps to get started:

## Prerequisites

- Python 3.13+
- Node.js 20+
- Neon DB account (for PostgreSQL database)

## Step 1: Set Up Neon DB (⚠️ REQUIRED)

1. Go to [https://neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Create a new database named `physical-ai-todo`
4. Copy the connection string (it looks like: `postgresql://user:password@ep-xxx.region.aws.neon.tech/physical-ai-todo`)

## Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your database URL and API keys
# DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/physical-ai-todo
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# CORS_ORIGINS=http://localhost:3000

# Run database migration
alembic upgrade head

# Start the backend server
python -m uvicorn app.main:app --reload
```

Backend will be running at: **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

## Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file from example
cp .env.local.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start the frontend development server
npm run dev
```

Frontend will be running at: **http://localhost:3000**

## Step 4: Verify Setup

1. Open http://localhost:8000/health - should return:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "service": "Physical AI Todo API"
   }
   ```

2. Open http://localhost:3000 - should show the Physical AI Todo homepage

## Next Steps

Once both servers are running, the implementation will continue with:
- ✅ Phase 1: Setup & Project Initialization (Complete)
- ✅ Phase 2: Foundation (Complete)
- ⏳ Phase 3: US1 - Basic Web CRUD (In Progress)
- ⏳ Phase 4-9: P2 Core Features
- ⏳ Phase 14: Testing & Deployment

## Troubleshooting

### Database connection fails
- Make sure your Neon DB connection string is correct in backend/.env
- Check that your Neon DB instance is active
- Verify your IP is allowed to connect (Neon allows all IPs by default)

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Verify CORS_ORIGINS in backend/.env includes http://localhost:3000

### Module import errors
- Make sure you've activated the Python virtual environment
- Run `pip install -r requirements.txt` again
- For frontend, run `npm install` again

## Project Structure

```
physical-ai-todo/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── models.py      # 7 database entities
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── database.py    # Neon DB connection
│   │   ├── main.py        # FastAPI app
│   │   ├── routes/        # API endpoints (to be created)
│   │   └── services/      # Business logic (to be created)
│   ├── alembic/           # Database migrations
│   └── requirements.txt
│
├── frontend/              # Next.js 14 frontend
│   ├── app/
│   │   ├── layout.tsx     # Root layout with dark mode
│   │   ├── page.tsx       # Homepage
│   │   └── globals.css    # Tailwind + theme variables
│   ├── components/        # React components (to be created)
│   ├── lib/
│   │   ├── types.ts       # TypeScript types
│   │   └── api.ts         # API client
│   └── package.json
│
└── specs/001-002-phase-2/ # Planning documents
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── ...
```

## Current Status

**Completed Tasks**: 
- Phase 1: 9/10 tasks (T007 requires manual Neon DB setup)
- Phase 2: 14/14 tasks ✓

**Total Progress**: 23/185 tasks (12%)

**Next Up**: Phase 3 - Basic Web CRUD implementation
