"""
Main API router that includes all endpoint routers
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    caregivers,
    clients,
    timelogs,
    shifts,
    documents,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(caregivers.router, prefix="/caregivers", tags=["Caregivers"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(timelogs.router, prefix="/timelogs", tags=["Time Tracking"])
api_router.include_router(shifts.router, prefix="/shifts", tags=["Scheduling"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"]) 