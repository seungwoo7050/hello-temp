_K='active'
_J='status'
_I='context'
_H='agent_id'
_G='last_accessed_at'
_F='user_id'
_E=None
_D='role'
_C='session_id'
_B='content'
_A='timestamp'
from app.schemas.session import Session,CreateSessionRequest,Message,SendMessageRequest,SendMessageResponse,SessionMemory,SessionDetailsResponse,SessionMemoryResponse
from app.services.vertex_session_adapter import VertexSessionAdapter
from app.core.config import settings
from typing import List,Optional,Dict,Any
from datetime import datetime,timedelta
import uuid,asyncio
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection
from bson import ObjectId
import json
from pymongo.errors import PyMongoError
class SessionService:
	def __init__(A,vertex_adapter=_E):
		A.vertex_adapter=vertex_adapter
		try:A.client=AsyncIOMotorClient(settings.MONGODB_URI);A.db=A.client[settings.MONGODB_DATABASE];A.sessions_collection=A.db['sessions'];A.short_term_memory_collection=A.db['short_term_memory'];A.long_term_memory_collection=A.db['long_term_memory'];asyncio.create_task(A._setup_indexes());print('SessionService initialized with MongoDB connection.')
		except Exception as B:print(f"Error connecting to MongoDB: {B}");raise RuntimeError(f"Failed to initialize MongoDB connection: {B}")
	async def _setup_indexes(A):await A.sessions_collection.create_index(_F);await A.sessions_collection.create_index(_H);await A.sessions_collection.create_index(_J);await A.sessions_collection.create_index(_G);await A.short_term_memory_collection.create_index(_C);await A.long_term_memory_collection.create_index(_F);await A.long_term_memory_collection.create_index([(_B,'text')])
	async def create_session(B,request):
		A=request;E=f"sess-{uuid.uuid4().hex}";C=_E
		if B.vertex_adapter:
			try:
				C=await B.vertex_adapter.create_vertex_session(agent_id_external=A.agent_id,user_id=A.user_id)
				if not C:print(f"Warning: Failed to create Vertex AI session for agent {A.agent_id}. Creating local session only.")
			except Exception as D:print(f"Error creating Vertex AI session: {D}")
		F=datetime.now();G=Session(id=E,agent_id=A.agent_id,user_id=A.user_id,vertex_session_id=C,status=_K,created_at=F,last_accessed_at=F,metadata=A.metadata or{})
		if A.initial_message:G.memory.short_term.add_message(A.initial_message);await B.short_term_memory_collection.insert_one({_C:E,_D:A.initial_message.role,_B:A.initial_message.content,_A:F})
		try:await B.sessions_collection.insert_one(G.dict(exclude={'memory'}));print(f"Session '{E}' created for agent '{A.agent_id}'. Vertex session: {C}");return G
		except PyMongoError as D:
			print(f"Error storing session in MongoDB: {D}")
			if C and B.vertex_adapter:
				try:await B.vertex_adapter.close_vertex_session(C)
				except Exception as H:print(f"Error cleaning up Vertex AI session: {H}")
			raise RuntimeError(f"Failed to create session: {D}")
	async def get_session(A,session_id):
		B=session_id
		try:
			F=await A.sessions_collection.find_one({'id':B})
			if not F:return
			C=datetime.now();await A.sessions_collection.update_one({'id':B},{'$set':{_G:C}});G=[]
			async for D in A.short_term_memory_collection.find({_C:B}).sort(_A,1):G.append(Message(role=D[_D],content=D[_B],timestamp=D.get(_A,C)))
			E=Session(**F);E.memory.short_term.messages=G;E.last_accessed_at=C;return E
		except PyMongoError as H:print(f"Error retrieving session from MongoDB: {H}");return
	async def send_message_to_agent(F,session_id,message_request):
		H='agent';I=message_request;C=session_id;A=await F.get_session(C)
		if not A or A.status!=_K:print(f"Session '{C}' not found or not active.");return
		J=datetime.now();D=Message(role=I.role,content=I.message_content,timestamp=J)
		try:await F.short_term_memory_collection.insert_one({_C:C,_D:D.role,_B:D.content,_A:J});A.memory.short_term.add_message(D)
		except PyMongoError as E:print(f"Error storing user message: {E}")
		B=_E
		if A.vertex_session_id and F.vertex_adapter:
			try:B=await F.vertex_adapter.query_vertex_session(vertex_session_id_or_name=A.vertex_session_id,user_message=D)
			except Exception as E:print(f"Error querying Vertex AI session: {E}");B=Message(role=H,content=f"Error connecting to AI agent: {str(E)}",timestamp=datetime.now())
		else:print(f"No Vertex AI session for session '{C}'. Using fallback agent.");B=Message(role=H,content=f"No AI agent connected to this session. Please connect an agent to process: {D.content}",timestamp=datetime.now())
		if B:
			try:
				await F.short_term_memory_collection.insert_one({_C:C,_D:B.role,_B:B.content,_A:B.timestamp or datetime.now()});A.memory.short_term.add_message(B)
				if I.store_in_long_term:await F._add_to_long_term_memory(user_id=A.user_id,content=B.content,context={_C:C,'user_message':D.content,_H:A.agent_id})
			except PyMongoError as E:print(f"Error storing agent reply: {E}")
			return SendMessageResponse(session_id=C,user_message=D,agent_reply=B,updated_memory=A.memory)
		else:
			G=Message(role=H,content='Error: Could not get a response from the agent.',timestamp=datetime.now())
			try:await F.short_term_memory_collection.insert_one({_C:C,_D:G.role,_B:G.content,_A:G.timestamp});A.memory.short_term.add_message(G)
			except PyMongoError as E:print(f"Error storing error message: {E}")
			return SendMessageResponse(session_id=C,user_message=D,agent_reply=G,updated_memory=A.memory)
	async def get_session_memory(B,session_id):
		A=await B.get_session(session_id)
		if A:return A.memory
	async def close_session(B,session_id):
		E='closed';C=session_id;A=await B.get_session(C)
		if not A:return
		try:
			F=datetime.now();await B.sessions_collection.update_one({'id':C},{'$set':{_J:E,_G:F}})
			if A.vertex_session_id and B.vertex_adapter:
				try:
					G=await B.vertex_adapter.close_vertex_session(A.vertex_session_id)
					if not G:print(f"Failed to close Vertex AI session for session '{C}'")
				except Exception as D:print(f"Error closing Vertex AI session: {D}")
			A.status=E;A.last_accessed_at=F;print(f"Session '{C}' closed.");return A
		except PyMongoError as D:print(f"Error closing session in MongoDB: {D}");return
	async def list_sessions(E,user_id=_E,agent_id=_E,skip=0,limit=100):
		F=agent_id;G=user_id
		try:
			A={}
			if G:A[_F]=G
			if F:A[_H]=F
			B=E.sessions_collection.find(A);B=B.sort(_G,-1).skip(skip).limit(limit);H=[]
			async for J in B:
				C=Session(**J);I=[]
				async for D in E.short_term_memory_collection.find({_C:C.id}).sort(_A,1):I.append(Message(role=D[_D],content=D[_B],timestamp=D.get(_A,datetime.now())))
				C.memory.short_term.messages=I;H.append(C)
			return H
		except PyMongoError as K:print(f"Error listing sessions from MongoDB: {K}");return[]
	async def _add_to_long_term_memory(A,user_id,content,context):
		'Add content to long-term memory for a user'
		try:await A.long_term_memory_collection.insert_one({_F:user_id,_B:content,_I:context,_A:datetime.now()});return True
		except PyMongoError as B:print(f"Error adding to long-term memory: {B}");return False
	async def query_long_term_memory(G,user_id,query,limit=5):
		'Query the long-term memory for a user';C='textScore';D='$meta';E='score'
		try:
			A=G.long_term_memory_collection.find({_F:user_id,'$text':{'$search':query}},{E:{D:C}});A=A.sort([(E,{D:C})]).limit(limit);F=[]
			async for B in A:F.append({_B:B[_B],_I:B[_I],_A:B[_A]})
			return F
		except PyMongoError as H:print(f"Error querying long-term memory: {H}");return[]