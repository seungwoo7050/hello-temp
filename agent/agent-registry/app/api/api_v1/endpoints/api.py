from fastapi import APIRouter
from app.api.api_v1.endpoints import registry
api_router=APIRouter()
api_router.include_router(registry.router,prefix='/registry',tags=['Agent Registry'])