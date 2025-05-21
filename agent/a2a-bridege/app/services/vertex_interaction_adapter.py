_A='projects/'
from google.cloud import aiplatform
from vertexai.agent_engines import AgentServiceClient
from app.core.config import settings
from typing import Optional,Tuple,Any,Dict
import uuid,logging
logger=logging.getLogger(__name__)
class VertexInteractionAdapter:
	def __init__(A):
		A.project_id=settings.VERTEX_PROJECT_ID;A.location=settings.VERTEX_LOCATION;A.client=None
		if A.project_id and A.location:
			try:aiplatform.init(project=A.project_id,location=A.location);A.client=AgentServiceClient(project=A.project_id,location=A.location);logger.info(f"VertexInteractionAdapter: Vertex AI SDK initialized for project {A.project_id}, location {A.location}")
			except Exception as B:logger.error(f"VertexInteractionAdapter: Failed to initialize Vertex client - {B}")
		else:logger.warning('VertexInteractionAdapter: project_id or location not set. Using simulation mode.')
	async def create_agent_vertex_session(A,agent_id_external,user_id=None):
		'\n        Create a session in Vertex AI for an agent and return the session name.\n        \n        Args:\n            agent_id_external: External ID of the agent\n            user_id: Optional user ID for session context\n            \n        Returns:\n            Vertex session name in format:\n            projects/{project}/locations/{location}/agents/{agent_id}/sessions/{session_id}\n        ';D=user_id;B=agent_id_external
		if not A.client:logger.warning('VertexInteractionAdapter: Client not initialized. Simulating session creation.');return f"simulated-vertex-session-for-{B}-{uuid.uuid4().hex}"
		try:
			F=f"projects/{A.project_id}/locations/{A.location}/agents/{B}";C={}
			if D:C['user_id']=D;C['source']='a2a-bridge'
			E=A.client.create_session(parent=F,session={'metadata':C});logger.info(f"VertexInteractionAdapter: Created Vertex AI session: {E.name}");return E.name
		except Exception as G:logger.error(f"VertexInteractionAdapter: Error creating session for agent {B} - {G}");return
	async def query_agent_vertex_session(C,vertex_session_name,prompt_for_agent):
		"\n        Send a prompt to a Vertex AI session and return the agent's response.\n        \n        Args:\n            vertex_session_name: Vertex AI session name\n            prompt_for_agent: Prompt text to send to the agent\n            \n        Returns:\n            Agent's response text\n        ";F=prompt_for_agent;B=vertex_session_name
		if not C.client:logger.warning(f"VertexInteractionAdapter: Client not initialized. Simulating query to session '{B}'.");return f"Simulated Vertex AI reply to: {F[:50]}..."
		try:
			D=B
			if not D.startswith(_A):logger.warning(f"Incomplete session name provided: {B} - Attempting to reconstruct");D=f"projects/{C.project_id}/locations/{C.location}/agents/{B.split("/")[0]}/sessions/{B.split("/")[1]}"
			H={'query':{'text':F}};logger.debug(f"Querying session {D} with prompt: {F[:100]}...");A=C.client.query_session(session=D,**H)
			if hasattr(A,'reply')and A.reply:E=A.reply.text
			else:
				logger.warning("Response structure doesn't contain expected 'reply.text' field");E='No response content found in agent reply'
				if hasattr(A,'response')and hasattr(A.response,'candidates'):
					for G in A.response.candidates:
						if hasattr(G,'content')and G.content:E=G.content;break
			logger.info(f"VertexInteractionAdapter: Received response from Vertex AI session (length: {len(E)})");return E
		except Exception as I:logger.error(f"VertexInteractionAdapter: Error querying session - {I}");return
	async def close_agent_vertex_session(A,vertex_session_name):
		'\n        Close a Vertex AI session\n        \n        Args:\n            vertex_session_name: Vertex AI session name to close\n            \n        Returns:\n            Boolean indicating success\n        ';B=vertex_session_name
		if not A.client:logger.warning(f"VertexInteractionAdapter: Client not initialized. Simulating session closing for '{B}'.");return True
		try:
			C=B
			if not C.startswith(_A):C=f"projects/{A.project_id}/locations/{A.location}/agents/{B.split("/")[0]}/sessions/{B.split("/")[1]}"
			A.client.delete_session(name=C);logger.info(f"VertexInteractionAdapter: Closed Vertex AI session '{C}'");return True
		except Exception as D:logger.error(f"VertexInteractionAdapter: Error closing session - {D}");return False