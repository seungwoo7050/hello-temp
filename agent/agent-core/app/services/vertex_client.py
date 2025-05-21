_H='history'
_G='update_time'
_F='create_time'
_E='session_id'
_D='agent_id'
_C='status'
_B='endpoint'
_A=None
from abc import ABC,abstractmethod
from typing import Dict,Any,List,Optional,cast
import uuid
from datetime import datetime
import logging,os,json,asyncio
from google.cloud import aiplatform
from google.cloud.aiplatform import VertexAI
from google.cloud.aiplatform.preview.agents import Agent as VertexAgent
from google.cloud.aiplatform.preview.agents import AgentServiceClient
from google.cloud.aiplatform.preview.agents import ExecutionConfig,AgentTool,Session
from google.cloud.aiplatform.preview.agents import SessionResponse
from google.cloud.aiplatform.preview.agents.state_machine import AgentStateMachine
from google.adk.orchestration import AgentOrchestrator
from google.api_core.exceptions import NotFound,PermissionDenied,InvalidArgument
from app.models.agent import AgentDefinition,Agent,AgentStatus,AgentTool as AppAgentTool
from app.core.config import settings
logger=logging.getLogger(__name__)
class VertexAIClientInterface(ABC):
	@abstractmethod
	async def authenticate(self):'Authenticate with Vertex AI'
	@abstractmethod
	async def create_agent_in_vertex(self,agent_definition):'Create an agent in Vertex AI. Returns created agent details.'
	@abstractmethod
	async def get_agent_from_vertex(self,agent_id):'Get agent details from Vertex AI'
	@abstractmethod
	async def list_agents_from_vertex(self,filters=_A):'List agents from Vertex AI'
	@abstractmethod
	async def deploy_agent_in_vertex(self,agent_id):'Deploy an agent in Vertex AI. Returns deployment status/info.'
	@abstractmethod
	async def delete_agent_from_vertex(self,agent_id):'Delete an agent from Vertex AI'
	@abstractmethod
	async def create_session_in_vertex(self,agent_id,user_id=_A):'Create a new session for an agent in Vertex AI'
	@abstractmethod
	async def query_session_in_vertex(self,session_id,query,agent_id=_A):'Send a query to an agent session in Vertex AI'
class VertexAIClient(VertexAIClientInterface):
	def __init__(A,project_id,location):B=location;C=project_id;A.project_id=C;A.location=B;A.agent_client=_A;A.orchestrator=_A;logger.info(f"Initializing VertexAIClient with project_id={C}, location={B}")
	async def _initialize_clients(A):
		'Initialize Vertex AI clients if not already initialized'
		if A.agent_client is _A:aiplatform.init(project=A.project_id,location=A.location);A.agent_client=AgentServiceClient(client_options={'api_endpoint':f"{A.location}-aiplatform.googleapis.com"});A.orchestrator=AgentOrchestrator(project=A.project_id,location=A.location,client=A.agent_client);logger.info('Vertex AI clients initialized successfully')
	async def authenticate(A):
		'Authenticate with Vertex AI'
		try:await A._initialize_clients();B=f"projects/{A.project_id}/locations/{A.location}";A.agent_client.list_agents(parent=B,page_size=1);logger.info('Successfully authenticated with Vertex AI')
		except Exception as C:logger.error(f"Authentication with Vertex AI failed: {C}");raise
	async def create_agent_in_vertex(D,agent_definition):
		'Create an agent in Vertex AI';A=agent_definition;await D._initialize_clients()
		try:
			G=f"projects/{D.project_id}/locations/{D.location}";E=[]
			if A.tools:
				for C in A.tools:H=AgentTool(display_name=C.name,description=C.description,function_declarations=C.schema,authentication_config=C.auth_config if hasattr(C,'auth_config')else _A);E.append(H)
			B=VertexAgent.create(display_name=A.name,description=A.description,tools=E,model=A.model,instructions=A.instructions,parent=G,language_codes=A.languages if hasattr(A,'languages')else['en'],serialized_graph=A.serialized_graph if hasattr(A,'serialized_graph')else _A);F=Agent(id=B.name.split('/')[-1],name=B.display_name,description=B.description,instructions=B.instructions,model_id=B.model,tools=[AppAgentTool(name=A.display_name,description=A.description,schema=A.function_declarations)for A in B.tools]if B.tools else[],status=AgentStatus.CREATED,created_at=datetime.now(),updated_at=datetime.now(),deployment_info=_A);logger.info(f"Agent '{F.id}' created successfully in Vertex AI");return F
		except Exception as I:logger.error(f"Failed to create agent in Vertex AI: {I}");raise
	async def get_agent_from_vertex(B,agent_id):
		'Get agent details from Vertex AI';C=agent_id;await B._initialize_clients()
		try:D=f"projects/{B.project_id}/locations/{B.location}/agents/{C}";A=B.agent_client.get_agent(name=D);E=Agent(id=A.name.split('/')[-1],name=A.display_name,description=A.description,instructions=A.instructions,model_id=A.model,tools=[AppAgentTool(name=A.display_name,description=A.description,schema=A.function_declarations)for A in A.tools]if A.tools else[],status=AgentStatus(A.state),created_at=A.create_time.ToDatetime()if hasattr(A,_F)else datetime.now(),updated_at=A.update_time.ToDatetime()if hasattr(A,_G)else datetime.now(),deployment_info={_B:A.endpoint}if hasattr(A,_B)else _A);logger.info(f"Agent '{C}' retrieved successfully from Vertex AI");return E
		except NotFound:logger.warning(f"Agent '{C}' not found in Vertex AI");return
		except Exception as F:logger.error(f"Failed to get agent '{C}' from Vertex AI: {F}");raise
	async def list_agents_from_vertex(B,filters=_A):
		'List agents from Vertex AI';G=filters;await B._initialize_clients()
		try:
			I=f"projects/{B.project_id}/locations/{B.location}";D=''
			if G:
				E=[]
				for(H,C)in G.items():
					if H=='name'and isinstance(C,str):E.append(f"display_name='{C}'")
					elif H==_C and isinstance(C,str):E.append(f"state='{C}'")
				D=' AND '.join(E)
			J=B.agent_client.list_agents(parent=I,filter=D if D else _A);F=[]
			for A in J:K=Agent(id=A.name.split('/')[-1],name=A.display_name,description=A.description,instructions=A.instructions,model_id=A.model,tools=[AppAgentTool(name=A.display_name,description=A.description,schema=A.function_declarations)for A in A.tools]if A.tools else[],status=AgentStatus(A.state),created_at=A.create_time.ToDatetime()if hasattr(A,_F)else datetime.now(),updated_at=A.update_time.ToDatetime()if hasattr(A,_G)else datetime.now(),deployment_info={_B:A.endpoint}if hasattr(A,_B)else _A);F.append(K)
			logger.info(f"Listed {len(F)} agents from Vertex AI");return F
		except Exception as L:logger.error(f"Failed to list agents from Vertex AI: {L}");raise
	async def deploy_agent_in_vertex(B,agent_id):
		'Deploy an agent in Vertex AI';A=agent_id;await B._initialize_clients()
		try:D=f"projects/{B.project_id}/locations/{B.location}/agents/{A}";E=B.agent_client.deploy_agent(name=D);C=E.result();F=C.endpoint if hasattr(C,_B)else _A;G={_D:A,_C:C.state,_B:F,'deployed_at':datetime.now().isoformat()};logger.info(f"Agent '{A}' deployed successfully in Vertex AI");return G
		except NotFound:logger.warning(f"Agent '{A}' not found for deployment in Vertex AI");return{_D:A,_C:'NOT_FOUND'}
		except Exception as H:logger.error(f"Failed to deploy agent '{A}' in Vertex AI: {H}");raise
	async def delete_agent_from_vertex(A,agent_id):
		'Delete an agent from Vertex AI';B=agent_id;await A._initialize_clients()
		try:C=f"projects/{A.project_id}/locations/{A.location}/agents/{B}";D=A.agent_client.delete_agent(name=C);D.result();logger.info(f"Agent '{B}' deleted successfully from Vertex AI");return True
		except NotFound:logger.warning(f"Agent '{B}' not found for deletion in Vertex AI");return False
		except Exception as E:logger.error(f"Failed to delete agent '{B}' from Vertex AI: {E}");raise
	async def create_session_in_vertex(B,agent_id,user_id=_A):
		'Create a new session for an agent in Vertex AI';D='user_id';C=user_id;A=agent_id;await B._initialize_clients()
		try:
			H=f"projects/{B.project_id}/locations/{B.location}/agents/{A}";E={}
			if C:E[D]=C
			F=Session.create(agent=H,session_metadata=E);G={_E:F.name.split('/')[-1],_D:A,D:C or'default_user','created_at':datetime.now().isoformat(),'session_path':F.name,_H:[]};logger.info(f"Session '{G[_E]}' created for agent '{A}' in Vertex AI");return G
		except NotFound:logger.warning(f"Agent '{A}' not found for session creation in Vertex AI");raise ValueError(f"Agent {A} not found for session creation.")
		except Exception as I:logger.error(f"Failed to create session for agent '{A}' in Vertex AI: {I}");raise
	async def query_session_in_vertex(B,session_id,query,agent_id=_A):
		'Send a query to an agent session in Vertex AI';H='tool_calls';I='agent';J='user';K=agent_id;L=query;D='content';E='role';A=session_id;await B._initialize_clients()
		try:
			if K:G=f"projects/{B.project_id}/locations/{B.location}/agents/{K}/sessions/{A}"
			elif A.startswith('projects/'):G=A
			else:
				M=await B.list_agents_from_vertex(filters={_C:'ACTIVE'})
				if not M:raise ValueError('No active agents found to query session.')
				Q=M[0].id;G=f"projects/{B.project_id}/locations/{B.location}/agents/{Q}/sessions/{A}"
			C=Session.detect_intent(session=G,text=L);N=C.response_text;F=[]
			if hasattr(C,'conversation_turns'):
				for O in C.conversation_turns:F.append({E:J,D:O.user_input});F.append({E:I,D:O.agent_response})
			else:F=[{E:J,D:L},{E:I,D:N}]
			P={_E:A,'reply':N,_H:F}
			if hasattr(C,H)and C.tool_calls:P[H]=[{'tool_name':A.name,'input':json.loads(A.input_text),'output':A.output}for A in C.tool_calls]
			logger.info(f"Session '{A}' queried successfully in Vertex AI");return P
		except NotFound:logger.warning(f"Session '{A}' not found in Vertex AI");raise ValueError(f"Session {A} not found.")
		except Exception as R:logger.error(f"Failed to query session '{A}' in Vertex AI: {R}");raise