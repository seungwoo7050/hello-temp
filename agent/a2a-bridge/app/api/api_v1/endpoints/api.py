from fastapi import APIRouter
from app.api.api_v1.endpoints import a2a
api_router=APIRouter()
api_router.include_router(a2a.router,prefix='/a2a',tags=['Agent-to-Agent (A2A) Communication'])