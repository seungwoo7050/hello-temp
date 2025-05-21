from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.dependencies import initialize_vertex_ai_for_a2a_bridge
app=FastAPI(title=settings.PROJECT_NAME,description='Service for facilitating Agent-to-Agent (A2A) communication, managing interaction state, and routing messages based on a defined A2A protocol.',version='0.1.0',openapi_url=f"{settings.API_V1_STR}/openapi.json",docs_url='/docs',redoc_url='/redoc')
if settings.BACKEND_CORS_ORIGINS:app.add_middleware(CORSMiddleware,allow_origins=[str(A)for A in settings.BACKEND_CORS_ORIGINS],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(api_router,prefix=settings.API_V1_STR)
@app.on_event('startup')
async def startup_event():
	'\n    Actions to perform on application startup.\n    - Initialize Vertex AI SDK (if used directly by A2A Bridge)\n    ';print('A2A Communication Bridge Service starting up...')
	if settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:initialize_vertex_ai_for_a2a_bridge()
@app.get('/health',tags=['Health'],summary='Service Health Check')
async def health_check():'\n    Checks the operational status of the A2A Communication Bridge service.\n    ';return{'status':'ok','service':'a2a-bridge','message':'A2A Bridge is healthy!'}
if __name__=='__main__':
	import uvicorn;default_port=8004
	try:service_port=int(os.getenv('PORT',str(default_port)))
	except ValueError:service_port=default_port
	print(f"Starting A2A Bridge service on host 0.0.0.0 port {service_port}");uvicorn.run('app.main:app',host='0.0.0.0',port=service_port,reload=True)