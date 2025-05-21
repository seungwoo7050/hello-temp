from functools import lru_cache
from app.core.config import settings
from app.services.vertex_client import VertexAIClientInterface,MockVertexAIClient,VertexAIService
from app.services.agent_service import AgentServiceInterface,MockAgentService,ConcreteAgentService
from app.services.orchestrator import OrchestratorInterface,MockOrchestrator,ConcreteOrchestratorService
USE_MOCK_SERVICES=False
@lru_cache()
def get_vertex_client():
	if USE_MOCK_SERVICES:print('Using MockVertexAIClient');return MockVertexAIClient()
	print('Using VertexAIService');return VertexAIService()
@lru_cache()
def get_agent_service():
	A=get_vertex_client()
	if USE_MOCK_SERVICES:print('Using MockAgentService');return MockAgentService(vertex_client=A)
	print('Using ConcreteAgentService');return ConcreteAgentService(vertex_client=A)
@lru_cache()
def get_orchestrator_service():
	A=get_vertex_client();B=get_agent_service()
	if USE_MOCK_SERVICES:print('Using MockOrchestrator');return MockOrchestrator(vertex_client=A,agent_service=B)
	print('Using ConcreteOrchestratorService')
	if isinstance(B,ConcreteAgentService)and isinstance(A,VertexAIService):return ConcreteOrchestratorService(vertex_client=A,agent_service=B)
	elif USE_MOCK_SERVICES and isinstance(B,MockAgentService)and isinstance(A,MockVertexAIClient):return MockOrchestrator(vertex_client=A,agent_service=B)
	else:
		print('Warning: Mismatch in service types for Orchestrator. Falling back to Mock if possible or raising error.')
		if isinstance(A,MockVertexAIClient)and isinstance(B,MockAgentService):return MockOrchestrator(vertex_client=A,agent_service=B)
		raise TypeError('Cannot instantiate ConcreteOrchestratorService with Mock services or vice-versa without proper configuration.')