from fastapi import APIRouter

from app.api.v1.endpoints import categories, milestones, stats, tasks

api_router = APIRouter()
api_router.include_router(tasks.router)
api_router.include_router(categories.router)
api_router.include_router(stats.router)
api_router.include_router(milestones.router)
