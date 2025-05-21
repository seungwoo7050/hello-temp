_T='pending_source_action'
_S='completed'
_R='is_complete'
_Q='message_content'
_P='timestamp'
_O='updated_at'
_N='primary_agent_ids'
_M='status'
_L='error_details'
_K='completion_reason'
_J='completion_status'
_I=False
_H='target_agent_id'
_G='source_agent_id'
_F='id'
_E='active'
_D='interaction_id'
_C='interactions_db'
_B=None
_A='_id'
from app.schemas.a2a import Interaction,InitiateInteractionRequest,InitiateInteractionResponse,A2AMessage,SendA2AMessageRequest,SendA2AMessageResponse,A2AMessageContent,DiscoveredAgent
from app.services.a2a_protocol_handler import A2AProtocolHandler
from app.services.agent_discovery_adapter import AgentDiscoveryAdapter
from app.services.vertex_interaction_adapter import VertexInteractionAdapter
from app.core.config import settings
from typing import List,Optional,Dict,Any
import uuid
from datetime import datetime
import logging,asyncio
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection
from pymongo.errors import PyMongoError
logger=logging.getLogger(__name__)
class A2ABridgeService:
	def __init__(A,protocol_handler,discovery_adapter,vertex_interaction_adapter,session_manager_adapter=_B,message_queue_client=_B):
		A.protocol_handler=protocol_handler;A.discovery_adapter=discovery_adapter;A.vertex_interaction_adapter=vertex_interaction_adapter;A.session_manager_adapter=session_manager_adapter;A.message_queue_client=message_queue_client
		try:A.client=AsyncIOMotorClient(settings.MONGODB_URI);A.db=A.client[settings.MONGODB_DATABASE];A.interactions_collection=A.db['interactions'];A.messages_collection=A.db['a2a_messages'];asyncio.create_task(A._setup_indexes());logger.info('A2ABridgeService initialized with MongoDB connection')
		except Exception as B:logger.error(f"Error connecting to MongoDB: {B}");A.interactions_db={};logger.warning('Using in-memory storage for interactions due to MongoDB connection failure')
	async def _setup_indexes(A):
		'Set up MongoDB indexes for efficient queries'
		try:await A.interactions_collection.create_index(_F,unique=True);await A.interactions_collection.create_index(_N);await A.interactions_collection.create_index('user_id');await A.interactions_collection.create_index(_M);await A.interactions_collection.create_index(_O);await A.messages_collection.create_index(_D);await A.messages_collection.create_index([(_G,1),(_H,1)]);await A.messages_collection.create_index(_P);logger.info('MongoDB indexes created for A2A Bridge collections')
		except PyMongoError as B:logger.error(f"Error creating MongoDB indexes: {B}")
	async def initiate_interaction(C,request):
		'\n        Initiate an A2A interaction between two agents.\n        \n        Args:\n            request: Interaction request with source agent, target agent, goal, and optional initial content\n            \n        Returns:\n            Response with interaction details and initial message\n            \n        Raises:\n            ValueError: If agents are not found\n            ConnectionError: If Vertex AI session creation fails\n        ';A=request;J=await C.discovery_adapter.find_agent_by_id(A.source_agent_id);K=await C.discovery_adapter.find_agent_by_id(A.target_agent_id)
		if not J or not K:
			H=[]
			if not J:H.append(A.source_agent_id)
			if not K:H.append(A.target_agent_id)
			logger.error(f"One or more agents not found in registry: {", ".join(H)}");raise ValueError(f"One or more agents not found in registry: {", ".join(H)}")
		D=f"int-{uuid.uuid4().hex}";O=datetime.now();B=Interaction(id=D,primary_agent_ids=[A.source_agent_id,A.target_agent_id],goal_description=A.goal,user_id=A.user_id,status='initializing',created_at=O,updated_at=O,agent_session_map={},message_history=[])
		try:await C.interactions_collection.insert_one(B.dict());logger.info(f"Created interaction {D} in database")
		except PyMongoError as E:
			logger.error(f"Error storing interaction in MongoDB: {E}")
			if hasattr(C,_C):C.interactions_db[D]=B;logger.warning(f"Stored interaction {D} in memory due to MongoDB error")
		F=[]
		if C.vertex_interaction_adapter:
			try:
				L=await C.vertex_interaction_adapter.create_agent_vertex_session(agent_id_external=A.source_agent_id,user_id=A.user_id)
				if L:B.agent_session_map[A.source_agent_id]=L;logger.info(f"Created Vertex session for source agent {A.source_agent_id}: {L}")
				else:F.append(f"Failed to create Vertex session for source agent {A.source_agent_id}")
			except Exception as E:F.append(f"Error creating Vertex session for source agent {A.source_agent_id}: {str(E)}")
			try:
				M=await C.vertex_interaction_adapter.create_agent_vertex_session(agent_id_external=A.target_agent_id,user_id=A.user_id)
				if M:B.agent_session_map[A.target_agent_id]=M;logger.info(f"Created Vertex session for target agent {A.target_agent_id}: {M}")
				else:F.append(f"Failed to create Vertex session for target agent {A.target_agent_id}")
			except Exception as E:F.append(f"Error creating Vertex session for target agent {A.target_agent_id}: {str(E)}")
			if F:B.status='failed_session_creation';B.metadata={'session_creation_errors':F};await C._update_interaction(B);logger.error(f"Session creation errors: {F}");raise ConnectionError(f"Failed to create Vertex AI sessions: {"; ".join(F)}")
		else:logger.warning('VertexInteractionAdapter not available. A2A interaction will proceed without Vertex AI sessions.')
		N=_B
		if C.vertex_interaction_adapter and A.source_agent_id in B.agent_session_map:
			R=B.agent_session_map[A.source_agent_id];P=C.protocol_handler.generate_initial_prompt_for_source_agent(source_agent_name=J.name,target_agent_name=K.name,goal=A.goal,interaction_id=D,initial_content=A.initial_message_content);logger.info(f"Sending initial prompt to source agent {A.source_agent_id}");logger.debug(f"Initial prompt: {P[:200]}...")
			try:
				Q=await C.vertex_interaction_adapter.query_agent_vertex_session(vertex_session_name=R,prompt_for_agent=P)
				if Q:
					I=await C.protocol_handler.parse_agent_response(response_text=Q,source_agent_id=A.source_agent_id,target_agent_id=A.target_agent_id,interaction_id=D);S=I[_Q];G=A2AMessage(id=f"msg-{uuid.uuid4().hex}",interaction_id=D,source_agent_id=A.source_agent_id,target_agent_id=A.target_agent_id,content=S,timestamp=datetime.now());await C._store_message(G);B.message_history.append(G)
					if I.get(_R,_I):B.status=_S;B.metadata={_J:I.get(_J),_K:I.get(_K)}
					else:B.status=_E
					N=G;logger.info(f"Received initial message from source agent for interaction {D}")
				else:logger.warning(f"Source agent {A.source_agent_id} did not provide an initial response");B.status=_T
			except Exception as E:logger.error(f"Error processing source agent response: {E}");B.status='error_processing_response';B.metadata={_L:str(E)}
		elif A.initial_message_content:G=A2AMessage(id=f"msg-{uuid.uuid4().hex}",interaction_id=D,source_agent_id=A.source_agent_id,target_agent_id=A.target_agent_id,content=A.initial_message_content,timestamp=datetime.now());await C._store_message(G);B.message_history.append(G);B.status=_E;N=G
		B.updated_at=datetime.now();await C._update_interaction(B)
		if C.message_queue_client:
			try:await C.message_queue_client.publish('a2a.interaction.created',{_D:D,_G:A.source_agent_id,_H:A.target_agent_id,_M:B.status})
			except Exception as E:logger.error(f"Error publishing message to queue: {E}")
		logger.info(f"A2A Interaction {D} initiated. Status: {B.status}");return InitiateInteractionResponse(interaction=B,initial_message_sent=N)
	async def route_message(B,interaction_id,source_agent_id,message_request):
		'\n        Route a message from one agent to another in an existing interaction.\n        \n        Args:\n            interaction_id: ID of the interaction\n            source_agent_id: ID of the source agent\n            message_request: Message request with content\n            \n        Returns:\n            Response with the sent message details\n            \n        Raises:\n            ValueError: If interaction not found or not in a valid state\n        ';N='reply_content';O='message_id';J='error_routing_message';K='waiting_for_response';E=source_agent_id;D=interaction_id;A=await B._get_interaction(D)
		if not A or A.status not in[_E,K,_T]:logger.error(f"Interaction {D} not found or not in a valid state");raise ValueError(f"Interaction {D} not found or not in a state to receive messages.")
		C=_B
		for P in A.primary_agent_ids:
			if P!=E:C=P;break
		if not C:logger.error(f"Could not determine target agent for interaction {D}");raise ValueError(f"Could not determine target agent for message in interaction {D}.")
		W=f"msg-{uuid.uuid4().hex}";Q=datetime.now();H=A2AMessage(id=W,interaction_id=D,source_agent_id=E,target_agent_id=C,content=message_request.content,timestamp=Q);await B._store_message(H);A.message_history.append(H);A.updated_at=Q;A.status='routing_message';await B._update_interaction(A);L=_B
		if B.vertex_interaction_adapter and C in A.agent_session_map:
			R=A.agent_session_map[C]
			try:
				S=await B.discovery_adapter.find_agent_by_id(E);T=await B.discovery_adapter.find_agent_by_id(C);X=S.name if S else E;Y=T.name if T else C;U=B.protocol_handler.wrap_content_for_target_agent(content_from_source=H.content,source_agent_name=X,target_agent_name=Y,interaction_id=D,goal=A.goal_description);logger.info(f"Routing message from {E} to {C} in session {R}");logger.debug(f"Prompt for target: {U[:200]}...");V=await B.vertex_interaction_adapter.query_agent_vertex_session(vertex_session_name=R,prompt_for_agent=U)
				if V:
					I=await B.protocol_handler.parse_agent_response(response_text=V,source_agent_id=C,target_agent_id=E,interaction_id=D);Z=I.get(_R,_I);a=I.get(_J);b=I.get(_K);G=A2AMessage(id=f"msg-{uuid.uuid4().hex}",interaction_id=D,source_agent_id=C,target_agent_id=E,content=I[_Q],timestamp=datetime.now());await B._store_message(G);A.message_history.append(G)
					if Z:A.status=_S;A.metadata={_J:a,_K:b}
					else:A.status=_E
					L=G;logger.info(f"Received response from target agent {C}")
					if B.message_queue_client:
						try:await B.message_queue_client.publish('a2a.message.received',{_D:D,O:G.id,_G:C,_H:E})
						except Exception as F:logger.error(f"Error publishing message to queue: {F}")
				else:logger.warning(f"No response received from target agent {C}");A.status=K
			except Exception as F:logger.error(f"Error processing message routing via Vertex AI: {F}");A.status=J;A.metadata={_L:str(F)}
		elif B.session_manager_adapter:
			try:
				logger.info(f"Routing message via Session Manager for interaction {D}");M=await B.session_manager_adapter.route_a2a_message(interaction_id=D,source_agent_id=E,target_agent_id=C,message_content=H.content)
				if M and M.get(N):G=A2AMessage(id=f"msg-{uuid.uuid4().hex}",interaction_id=D,source_agent_id=C,target_agent_id=E,content=M[N],timestamp=datetime.now());await B._store_message(G);A.message_history.append(G);A.status=_E;L=G;logger.info(f"Received response via Session Manager from {C}")
				else:logger.warning(f"No response received via Session Manager from {C}");A.status=K
			except Exception as F:logger.error(f"Error routing message via Session Manager: {F}");A.status=J;A.metadata={_L:str(F)}
		elif B.message_queue_client:
			try:logger.info(f"Publishing message to queue for async processing for interaction {D}");await B.message_queue_client.publish('a2a.message.route',{_D:D,O:H.id,_G:E,_H:C});A.status='message_queued'
			except Exception as F:logger.error(f"Error publishing message to queue: {F}");A.status=J;A.metadata={_L:str(F)}
		else:logger.warning(f"No routing method available for interaction {D}");A.status='routing_not_available'
		A.updated_at=datetime.now();await B._update_interaction(A);return SendA2AMessageResponse(message_sent=H,response_message=L)
	async def get_interaction_details(A,interaction_id):'Get details of an interaction by ID';return await A._get_interaction(interaction_id)
	async def list_interactions(B,agent_id=_B,status=_B,limit=100,skip=0):
		'\n        List interactions with optional filtering\n        \n        Args:\n            agent_id: Filter by agent ID\n            status: Filter by interaction status\n            limit: Maximum number of interactions to return\n            skip: Number of interactions to skip (for pagination)\n            \n        Returns:\n            List of interactions matching the criteria\n        ';J=limit;E=skip;C=status;D=agent_id
		try:
			F={}
			if D:F[_N]=D
			if C:F[_M]=C
			G=B.interactions_collection.find(F);G=G.sort(_O,-1).skip(E).limit(J);K=[]
			async for A in G:
				if _A in A:A[_A]=str(A[_A])
				M=await B._get_interaction_messages(A[_F]);L=Interaction(**A);L.message_history=M;K.append(L)
			return K
		except PyMongoError as N:
			logger.error(f"Error listing interactions from MongoDB: {N}")
			if hasattr(B,_C):
				logger.warning('Falling back to in-memory storage for listing interactions');H=[]
				for I in B.interactions_db.values():
					if D and D not in I.primary_agent_ids:continue
					if C and I.status!=C:continue
					H.append(I)
				H.sort(key=lambda i:i.updated_at,reverse=True);return H[E:E+J]
			return[]
	async def discover_a2a_agents(A):'Discover agents capable of A2A communication';return await A.discovery_adapter.list_available_a2a_agents()
	async def _get_interaction(B,interaction_id):
		'Get an interaction from the database';A=interaction_id
		try:
			C=await B.interactions_collection.find_one({_F:A})
			if not C:
				logger.warning(f"Interaction {A} not found in database")
				if hasattr(B,_C)and A in B.interactions_db:return B.interactions_db[A]
				return
			if _A in C:C[_A]=str(C[_A])
			E=await B._get_interaction_messages(A);D=Interaction(**C);D.message_history=E;return D
		except PyMongoError as F:
			logger.error(f"Error getting interaction {A} from MongoDB: {F}")
			if hasattr(B,_C)and A in B.interactions_db:logger.warning(f"Falling back to in-memory storage for interaction {A}");return B.interactions_db[A]
			return
	async def _update_interaction(B,interaction):
		'Update an interaction in the database';A=interaction
		try:
			C=await B.interactions_collection.update_one({_F:A.id},{'$set':A.dict(exclude={'message_history'})});D=C.modified_count>0 or C.matched_count>0
			if not D:logger.warning(f"Failed to update interaction {A.id} in MongoDB")
			if hasattr(B,_C):B.interactions_db[A.id]=A
			return D
		except PyMongoError as E:
			logger.error(f"Error updating interaction {A.id} in MongoDB: {E}")
			if hasattr(B,_C):B.interactions_db[A.id]=A;logger.warning(f"Updated interaction {A.id} in memory due to MongoDB error");return True
			return _I
	async def _store_message(A,message):
		'Store an A2A message in the database'
		try:B=message.dict();C=await A.messages_collection.insert_one(B);return bool(C.inserted_id)
		except PyMongoError as D:logger.error(f"Error storing message in MongoDB: {D}");return _I
	async def _get_interaction_messages(E,interaction_id):
		'Get all messages for an interaction';C=interaction_id
		try:
			B=E.messages_collection.find({_D:C});B=B.sort(_P,1);D=[]
			async for A in B:
				if _A in A:A[_A]=str(A[_A])
				F=A2AMessage(**A);D.append(F)
			return D
		except PyMongoError as G:logger.error(f"Error getting messages for interaction {C} from MongoDB: {G}");return[]