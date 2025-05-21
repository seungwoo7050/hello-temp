from functools import lru_cache
from vertexai import init as vertex_init
from google.auth import default as default_auth
from google.auth.exceptions import DefaultCredentialsError
from app.core.config import settings
from app.services.capability_registry_store import CapabilityRegistryStore
from app.services.vertex_service_client_adapter import VertexServiceClientAdapter
from app.services.registry_service import AgentRegistryService
_vertex_ai_initialized_registry=False
def initialize_vertex_ai_for_registry():
	global _vertex_ai_initialized_registry
	if not _vertex_ai_initialized_registry and settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		try:print(f"Initializing Vertex AI for Agent Registry: Project ID: {settings.VERTEX_PROJECT_ID}, Location: {settings.VERTEX_LOCATION}");A,C=default_auth();vertex_init(project=settings.VERTEX_PROJECT_ID,location=settings.VERTEX_LOCATION,credentials=A);_vertex_ai_initialized_registry=True;print('Vertex AI SDK initialized successfully for Agent Registry.')
		except DefaultCredentialsError:print('ERROR: Google Cloud Default Credentials not found for Agent Registry.')
		except Exception as B:print(f"ERROR: Failed to initialize Vertex AI SDK for Agent Registry: {B}")
@lru_cache()
def get_capability_registry_store():return CapabilityRegistryStore()
@lru_cache()
def get_vertex_service_client_adapter():
	if settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		if not _vertex_ai_initialized_registry:print('Warning: Vertex AI SDK for registry might not be initialized when get_vertex_service_client_adapter is called first.')
		return VertexServiceClientAdapter()
@lru_cache()
def get_registry_service():A=get_capability_registry_store();B=get_vertex_service_client_adapter();return AgentRegistryService(capability_store=A,vertex_adapter=B)