from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.api.api_v1.api import api_router
app=FastAPI(title=settings.PROJECT_NAME,description='FastAPI service for agent-core. Manages AI agents and orchestrates multi-agent workflows using Vertex AI and ADK.',version='0.1.0',openapi_url=f"{settings.API_V1_STR}/openapi.json",docs_url='/docs',redoc_url='/redoc')
if settings.BACKEND_CORS_ORIGINS:app.add_middleware(CORSMiddleware,allow_origins=[str(A)for A in settings.BACKEND_CORS_ORIGINS],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(api_router,prefix=settings.API_V1_STR)
@app.on_event('startup')
async def startup_event():
	'\n    Actions to perform on application startup.\n    - Initialize Vertex AI Client (authenticate)\n    - Potentially connect to DB, Message Queue\n    ';print('Agent Core Service starting up...')
	try:
		from app.core.dependencies import get_vertex_client as B;A=B()
		if hasattr(A,'authenticate')and not dependencies.USE_MOCK_SERVICES:await A.authenticate()
		print('VertexAIClient obtained and potentially authenticated on startup.')
	except Exception as C:print(f"Error during startup (Vertex AI client initialization): {C}")
@app.get('/health',tags=['Health'],summary='Service Health Check')
async def health_check():'\n    Checks the operational status of the Agent Core service.\n    ';return{'status':'ok','service':'agent-core','message':'Agent Core is healthy!'}
if __name__=='__main__':
	import uvicorn;default_port=8000
	try:
		service_port=int(os.getenv('PORT',str(default_port)))
		if service_port!=default_port:print(f"Warning: PORT environment variable is set to {service_port}, but agent-core is typically run on {default_port} in this project structure. Ensure no port conflicts.")
	except ValueError:service_port=default_port
	print(f"Starting Agent Core service on host 0.0.0.0 port {service_port}");uvicorn.run('app.main:app',host='0.0.0.0',port=service_port,reload=True)