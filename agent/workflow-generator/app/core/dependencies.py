from functools import lru_cache
from vertexai import init as vertex_init
from google.auth import default as default_auth
from google.auth.exceptions import DefaultCredentialsError
from app.core.config import settings
from app.services.llm_service import LLMService
from app.services.langgraph_service import LangGraphService
from app.services.workflow_service import WorkflowService
_vertex_ai_initialized=False
def initialize_vertex_ai():
	global _vertex_ai_initialized
	if not _vertex_ai_initialized:
		try:
			print(f"Initializing Vertex AI with Project ID: {settings.VERTEX_PROJECT_ID}, Location: {settings.VERTEX_LOCATION}");B,A=default_auth()
			if settings.VERTEX_PROJECT_ID and A!=settings.VERTEX_PROJECT_ID:print(f"Warning: Environment's default project ('{A}') differs from settings.VERTEX_PROJECT_ID ('{settings.VERTEX_PROJECT_ID}'). Using settings value.")
			vertex_init(project=settings.VERTEX_PROJECT_ID,location=settings.VERTEX_LOCATION,credentials=B);_vertex_ai_initialized=True;print('Vertex AI SDK initialized successfully for Workflow Generator.')
		except DefaultCredentialsError:print('ERROR: Google Cloud Default Credentials not found for Workflow Generator. Ensure you are authenticated.')
		except Exception as C:print(f"ERROR: Failed to initialize Vertex AI SDK for Workflow Generator: {C}")
@lru_cache()
def get_llm_service():
	if not _vertex_ai_initialized:print('Warning: Vertex AI SDK might not be initialized when get_llm_service is called first time without app startup.')
	return LLMService(model_id=settings.DEFAULT_LLM_MODEL_ID)
@lru_cache()
def get_langgraph_service():return LangGraphService()
@lru_cache()
def get_workflow_service():A=get_llm_service();B=get_langgraph_service();return WorkflowService(llm_service=A,langgraph_service=B)