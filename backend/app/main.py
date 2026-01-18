"""FastAPI application entry point with CORS middleware and health check"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import attachments, notes, subtasks
from app.auth import routes as auth
from app.database import init_db
from app.routes import chat, tasks, notifications
from app.scheduler import start_scheduler, shutdown_scheduler

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    print("Starting Physical AI Todo API")
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
    print("Starting background scheduler...")
    start_scheduler()
    print("Background scheduler started successfully")
    yield
    # Shutdown
    print("Shutting down Physical AI Todo API")
    print("Stopping background scheduler...")
    shutdown_scheduler()
    print("Background scheduler stopped")


# Initialize FastAPI app
app = FastAPI(
    title="Physical AI Todo API",
    description="Full-stack todo application with AI-powered features",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS - get allowed origins from environment or use default
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3001,http://localhost:3000,http://todo.local,http://161-35-250-151.nip.io")
cors_origins_list = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,  # Allow origins from environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Auth routes (public)
app.include_router(tasks.router)  # Task routes (protected)
app.include_router(subtasks.router)  # Subtask routes (protected)
app.include_router(notes.router)  # Note routes (protected)
app.include_router(attachments.router)  # Attachment routes (protected)
app.include_router(chat.router, prefix="/api/v1")  # Chat routes (protected) - Phase III
app.include_router(notifications.router)  # Notification routes (protected) - Phase VI


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0", "service": "Physical AI Todo API"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Physical AI Todo API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
