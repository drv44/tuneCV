from fastapi import APIRouter

from .endpoints import resumes

api_router = APIRouter()
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])

# Add other routers here if you have more endpoint modules
# e.g., api_router.include_router(users.router, prefix="/users", tags=["users"]) 