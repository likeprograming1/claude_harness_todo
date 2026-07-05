from fastapi import APIRouter

from app.api.v1.endpoints.connectors import router as connectors_router
from app.api.v1.endpoints.harness_drawings import router as drawings_router
from app.api.v1.endpoints.wires import router as wires_router

api_router = APIRouter()
api_router.include_router(wires_router)
api_router.include_router(connectors_router)
api_router.include_router(drawings_router)
