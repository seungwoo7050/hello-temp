from fastapi import APIRouter
from app.api.api_v1.endpoints import agents,orchestration
api_router=APIRouter()
api_router.include_router(agents.router,prefix='/agents',tags=['Agents'])
api_router.include_router(orchestration.router,prefix='/orchestration',tags=['Agent Orchestration'])