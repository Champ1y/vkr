from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.ask import router as ask_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.versions import router as versions_router

api_router = APIRouter(prefix="/api")
api_router.include_router(ask_router)
api_router.include_router(health_router)
api_router.include_router(versions_router)
api_router.include_router(history_router)
api_router.include_router(admin_router)
