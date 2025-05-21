import secrets
from typing import List,Optional,Union
from pydantic import AnyHttpUrl,BaseSettings,validator,Field
class Settings(BaseSettings):
	API_V1_STR:str='/api/v1';SECRET_KEY:str=secrets.token_urlsafe(32);PROJECT_NAME:str='hello-dynamic-agents-agent-registry';BACKEND_CORS_ORIGINS:List[AnyHttpUrl]=['http://localhost:3000']
	@validator('BACKEND_CORS_ORIGINS',pre=True)
	def assemble_cors_origins(cls,v):
		if isinstance(v,str)and not v.startswith('['):return[A.strip()for A in v.split(',')]
		elif isinstance(v,(list,str)):return v
		raise ValueError(v)
	VERTEX_PROJECT_ID:Optional[str]=Field(None,env='VERTEX_PROJECT_ID');VERTEX_LOCATION:Optional[str]=Field(None,env='VERTEX_LOCATION');MATCHING_LLM_MODEL_ID:Optional[str]=Field('gemini-1.5-pro-latest',env='MATCHING_LLM_MODEL_ID');AGENT_CORE_SERVICE_URL:Optional[str]=Field('http://agent-core:8000/api/v1',env='AGENT_CORE_SERVICE_URL')
	class Config:case_sensitive=True;env_file='.env';env_file_encoding='utf-8'
settings=Settings()