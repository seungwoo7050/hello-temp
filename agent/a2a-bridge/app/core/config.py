import secrets
from typing import List,Optional,Union
from pydantic import AnyHttpUrl,BaseSettings,validator,Field
class Settings(BaseSettings):
	API_V1_STR:str='/api/v1';SECRET_KEY:str=secrets.token_urlsafe(32);PROJECT_NAME:str='hello-dynamic-agents-a2a-bridge';BACKEND_CORS_ORIGINS:List[AnyHttpUrl]=['http://localhost:3000']
	@validator('BACKEND_CORS_ORIGINS',pre=True)
	def assemble_cors_origins(cls,v):
		if isinstance(v,str)and not v.startswith('['):return[A.strip()for A in v.split(',')]
		elif isinstance(v,(list,str)):return v
		raise ValueError(v)
	VERTEX_PROJECT_ID:Optional[str]=Field(None,env='VERTEX_PROJECT_ID');VERTEX_LOCATION:Optional[str]=Field(None,env='VERTEX_LOCATION');AGENT_REGISTRY_SERVICE_URL:str=Field('http://agent-registry:8002/api/v1',env='AGENT_REGISTRY_SERVICE_URL');SESSION_MANAGER_SERVICE_URL:str=Field('http://session-manager:8003/api/v1',env='SESSION_MANAGER_SERVICE_URL')
	class Config:case_sensitive=True;env_file='.env';env_file_encoding='utf-8'
settings=Settings()