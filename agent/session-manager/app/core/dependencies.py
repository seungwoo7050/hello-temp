from functools import lru_cache
from vertexai import init as vertex_init
from google.auth import default as default_auth
from google.auth.exceptions import DefaultCredentialsError
from app.core.config import settings
from app.services.vertex_session_adapter import VertexSessionAdapter
from app.services.session_service import SessionService
_vertex_ai_initialized_session_mgr=False
def initialize_vertex_ai_for_session_manager():
	global _vertex_ai_initialized_session_mgr
	if not _vertex_ai_initialized_session_mgr and settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		try:print(f"Initializing Vertex AI for Session Manager: Project ID: {settings.VERTEX_PROJECT_ID}, Location: {settings.VERTEX_LOCATION}");A,C=default_auth();vertex_init(project=settings.VERTEX_PROJECT_ID,location=settings.VERTEX_LOCATION,credentials=A);_vertex_ai_initialized_session_mgr=True;print('Vertex AI SDK initialized successfully for Session Manager.')
		except DefaultCredentialsError:print('ERROR: Google Cloud Default Credentials not found for Session Manager.')
		except Exception as B:print(f"ERROR: Failed to initialize Vertex AI SDK for Session Manager: {B}")
@lru_cache()
def get_vertex_session_adapter():
	if settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		if not _vertex_ai_initialized_session_mgr:print('Warning: Vertex AI SDK for session manager might not be initialized when get_vertex_session_adapter is called first.')
		return VertexSessionAdapter()
@lru_cache()
def get_session_service():A=get_vertex_session_adapter();return SessionService(vertex_adapter=A)