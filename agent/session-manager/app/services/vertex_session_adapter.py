_A='projects/'
import uuid
from typing import Optional,Dict,Any,Tuple
from google.cloud import aiplatform
from vertexai.agent_engines import AgentServiceClient
from app.core.config import settings
from app.schemas.session import Message
class VertexSessionAdapter:
	def __init__(A):
		A.project_id=settings.VERTEX_PROJECT_ID;A.location=settings.VERTEX_LOCATION;A.client=None
		if A.project_id and A.location:
			try:aiplatform.init(project=A.project_id,location=A.location);A.client=AgentServiceClient(project=A.project_id,location=A.location);print(f"VertexSessionAdapter: Vertex AI SDK initialized for project {A.project_id}, location {A.location}.")
			except Exception as B:print(f"VertexSessionAdapter: Failed to initialize Vertex client - {B}")
		else:print('VertexSessionAdapter: project_id or location not set, Vertex AI client not initialized.')
	async def create_vertex_session(A,agent_id_external,user_id=None):
		'\n        Create a session in Vertex AI and return the Vertex AI session name.\n        \n        Args:\n            agent_id_external: External ID of the agent\n            user_id: Optional user ID\n            \n        Returns:\n            Vertex session name in format:\n            projects/{project}/locations/{location}/agents/{agent_id}/sessions/{session_id}\n        ';B=user_id
		if not A.client:print('VertexSessionAdapter: Client not initialized. Simulating session creation.');return f"sim-vertex-sess-{uuid.uuid4().hex}"
		try:
			E=f"projects/{A.project_id}/locations/{A.location}/agents/{agent_id_external}";C={}
			if B:C['user_id']=B
			D=A.client.create_session(parent=E,session={'metadata':C});print(f"VertexSessionAdapter: Created Vertex AI session: {D.name}");return D.name
		except Exception as F:print(f"VertexSessionAdapter: Error creating session - {F}");return
	async def query_vertex_session(C,vertex_session_id_or_name,user_message):
		"\n        Send a user message to a Vertex AI session and return the agent's response.\n        \n        Args:\n            vertex_session_id_or_name: Vertex AI session name or ID\n            user_message: User message to send\n            \n        Returns:\n            Agent's response as a Message object\n        ";G=user_message;H=vertex_session_id_or_name;D='agent'
		if not C.client:print(f"VertexSessionAdapter: Client not initialized. Simulating query to session '{H}'.");return Message(role=D,content=f"Simulated AI reply to: {G.content}")
		try:
			A=H
			if not A.startswith(_A):A=f"projects/{C.project_id}/locations/{C.location}/agents/{A.split("/")[0]}/sessions/{A.split("/")[1]}"
			J={'query':{'text':G.content}};B=C.client.query_session(session=A,**J)
			if hasattr(B,'reply')and B.reply:E=B.reply.text
			else:
				E='No response content found in agent reply'
				if hasattr(B,'response')and hasattr(B.response,'candidates'):
					for F in B.response.candidates:
						if hasattr(F,'content')and F.content:E=F.content;break
			print(f"VertexSessionAdapter: Received response from Vertex AI session '{A}'");return Message(role=D,content=E)
		except Exception as I:print(f"VertexSessionAdapter: Error querying session - {I}");return Message(role=D,content=f"Error getting response from AI agent: {str(I)}")
	async def close_vertex_session(B,vertex_session_id_or_name):
		'\n        Close a Vertex AI session\n        \n        Args:\n            vertex_session_id_or_name: Vertex AI session name or ID\n            \n        Returns:\n            Boolean indicating success\n        ';C=vertex_session_id_or_name
		if not B.client:print(f"VertexSessionAdapter: Client not initialized. Simulating session closing for '{C}'.");return True
		try:
			A=C
			if not A.startswith(_A):A=f"projects/{B.project_id}/locations/{B.location}/agents/{A.split("/")[0]}/sessions/{A.split("/")[1]}"
			B.client.delete_session(name=A);print(f"VertexSessionAdapter: Closed Vertex AI session '{A}'");return True
		except Exception as D:print(f"VertexSessionAdapter: Error closing session - {D}");return False