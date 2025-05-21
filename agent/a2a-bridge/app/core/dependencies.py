from functools import lru_cache
from vertexai import init as vertex_init
from google.auth import default as default_auth
from google.auth.exceptions import DefaultCredentialsError
from app.core.config import settings
from app.services.a2a_protocol_handler import A2AProtocolHandler
from app.services.agent_discovery_adapter import AgentDiscoveryAdapter
from app.services.vertex_interaction_adapter import VertexInteractionAdapter
from app.services.a2a_bridge_service import A2ABridgeService
_vertex_ai_initialized_a2a=False
def initialize_vertex_ai_for_a2a_bridge():
	global _vertex_ai_initialized_a2a
	if not _vertex_ai_initialized_a2a and settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		try:print(f"Initializing Vertex AI for A2A Bridge: Project ID: {settings.VERTEX_PROJECT_ID}, Location: {settings.VERTEX_LOCATION}");A,C=default_auth();vertex_init(project=settings.VERTEX_PROJECT_ID,location=settings.VERTEX_LOCATION,credentials=A);_vertex_ai_initialized_a2a=True;print('Vertex AI SDK initialized successfully for A2A Bridge.')
		except DefaultCredentialsError:print('ERROR: Google Cloud Default Credentials not found for A2A Bridge.')
		except Exception as B:print(f"ERROR: Failed to initialize Vertex AI SDK for A2A Bridge: {B}")
@lru_cache()
def get_a2a_protocol_handler():return A2AProtocolHandler()
@lru_cache()
def get_agent_discovery_adapter():return AgentDiscoveryAdapter()
@lru_cache()
def get_vertex_interaction_adapter():
	if settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
		if not _vertex_ai_initialized_a2a:print('Warning: Vertex AI SDK for A2A Bridge might not be initialized when get_vertex_interaction_adapter is called.')
		return VertexInteractionAdapter()
@lru_cache()
def get_a2a_bridge_service():A=get_a2a_protocol_handler();B=get_agent_discovery_adapter();C=get_vertex_interaction_adapter();return A2ABridgeService(protocol_handler=A,discovery_adapter=B,vertex_interaction_adapter=C)