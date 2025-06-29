from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.patients.router import router as patients_router
# Import other routers as they are created
# from app.api.v1.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])
# Include other routers as they are created
# api_router.include_router(users_router, prefix="/users", tags=["Users"]) 