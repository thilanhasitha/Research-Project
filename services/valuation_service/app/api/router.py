from fastapi import APIRouter

from app.api.routes import cse, health, valuation

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router)
api_router.include_router(cse.router)
api_router.include_router(valuation.router)
