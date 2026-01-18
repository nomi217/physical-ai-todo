"""
Health Check Endpoint for Kubernetes Probes
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    service: str = "todo-backend"


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for Kubernetes liveness and readiness probes.

    Returns:
        HealthResponse with status and timestamp
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/ready", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint - can be extended to check database connection.

    Returns:
        HealthResponse indicating service is ready to accept traffic
    """
    # TODO: Add database connection check here
    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow().isoformat()
    )
