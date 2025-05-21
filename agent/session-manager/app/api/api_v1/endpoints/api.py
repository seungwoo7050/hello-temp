from fastapi import APIRouter
from app.api.api_v1.endpoints import sessions
api_router=APIRouter()
api_router.include_router(sessions.router,prefix='/sessions',tags=['Sessions'])