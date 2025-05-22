from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.internal_data import init_data
init_data()
app=FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION,openapi_url='/api/v1/openapi.json')
if settings.ALLOWED_ORIGINS:app.add_middleware(CORSMiddleware,allow_origins=[str(A)for A in settings.ALLOWED_ORIGINS],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(api_router,prefix='/api/v1')
@app.get('/health',tags=['Health Check'])
async def health_check():return{'status':'ok','name':settings.PROJECT_NAME,'version':settings.PROJECT_VERSION}