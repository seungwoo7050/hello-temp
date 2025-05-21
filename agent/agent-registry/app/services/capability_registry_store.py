_F='agent_id_external'
_E='name'
_D='id'
_C='capabilities'
_B='agent_id'
_A='_id'
from app.schemas.capability import RegisteredAgent,Capability,CapabilityMatchRequest
from typing import List,Dict,Optional,Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from datetime import datetime
import uuid
from vertexai.generative_models import GenerativeModel,GenerationConfig
import json,re
class CapabilityRegistryStore:
	def __init__(A):A.client=AsyncIOMotorClient(settings.MONGODB_URI);A.db=A.client[settings.MONGODB_DATABASE];A.agents_collection=A.db['registered_agents'];A.capabilities_collection=A.db[_C];A._init_indexes();A.generative_model=GenerativeModel(settings.DEFAULT_LLM_MODEL_ID);print('CapabilityRegistryStore initialized with MongoDB.')
	async def _init_indexes(A):'Create necessary indexes for collections';await A.agents_collection.create_index(_D,unique=True);await A.agents_collection.create_index(_F,unique=True);await A.agents_collection.create_index(_E);await A.capabilities_collection.create_index(_B);await A.capabilities_collection.create_index(_E)
	async def register_agent(B,agent_data):
		'Register a new agent with its capabilities';A=agent_data
		if not A.id:A.id=str(uuid.uuid4())
		D=datetime.now();A.created_at=A.created_at or D;A.updated_at=D;E=A.capabilities;G=A.dict(exclude={_C});await B.agents_collection.replace_one({_D:A.id},G,upsert=True);await B.capabilities_collection.delete_many({_B:A.id})
		if E:
			C=[]
			for H in E:F=H.dict();F[_B]=A.id;C.append(F)
			if C:await B.capabilities_collection.insert_many(C)
		print(f"Agent '{A.name}' (ID: {A.id}) registered in CapabilityRegistryStore.");return A
	async def get_agent_by_id(C,registry_id):
		'Get agent by internal registry ID with capabilities';D=registry_id;A=await C.agents_collection.find_one({_D:D})
		if not A:return
		E=[]
		async for B in C.capabilities_collection.find({_B:D}):
			del B[_B]
			if _A in B:del B[_A]
			E.append(Capability(**B))
		if _A in A:del A[_A]
		A[_C]=E;return RegisteredAgent(**A)
	async def get_agent_by_external_id(C,agent_id_external):
		'Get agent by external provider ID';A=await C.agents_collection.find_one({_F:agent_id_external})
		if not A:return
		D=[]
		async for B in C.capabilities_collection.find({_B:A[_D]}):
			del B[_B]
			if _A in B:del B[_A]
			D.append(Capability(**B))
		if _A in A:del A[_A]
		A[_C]=D;return RegisteredAgent(**A)
	async def list_all_agents(C,skip=0,limit=100):
		'List all registered agents with pagination';D=[];F=C.agents_collection.find().skip(skip).limit(limit)
		async for A in F:
			if _A in A:del A[_A]
			E=[]
			async for B in C.capabilities_collection.find({_B:A[_D]}):
				del B[_B]
				if _A in B:del B[_A]
				E.append(Capability(**B))
			A[_C]=E;D.append(RegisteredAgent(**A))
		return D
	async def _extract_capabilities_from_task(E,task_description):
		'Extract required capabilities from a task description using LLM';B=task_description
		try:
			F=f'''
            Extract the required capabilities and tools needed to complete this task:
            
            TASK: {B}
            
            Return ONLY a JSON array of capability strings. Each capability should be a single word or 
            short phrase describing a skill or tool needed. Examples: "web_search", "text_analysis", 
            "image_generation", "code_writing".
            
            EXAMPLE OUTPUT FORMAT:
            ["web_search", "text_summarization", "data_analysis"]
            ''';G=await E.generative_model.generate_content_async(F,generation_config=GenerationConfig(temperature=.2,response_mime_type='application/json',max_output_tokens=256));A=G.text
			if'```json'in A:A=re.search('```json\\s*(.*?)\\s*```',A,re.DOTALL).group(1)
			H=json.loads(A);return[A.lower()for A in H if isinstance(A,str)]
		except Exception as I:
			print(f"Error extracting capabilities: {I}");C=set();J=['analyze','search','generate','create','write','translate','summarize','extract','code','image','audio','video']
			for D in J:
				if D in B.lower():C.add(D)
			return list(C)
	async def find_matching_agents(K,match_request):
		'Find agents matching the requirements with semantic matching';Q='$capabilities';R='$addFields';S='$match';L='score';E='i';F='$options';G='$regex';H='$or';B=match_request;T=[];I=[];M=[]
		if B.task_description:I=await K._extract_capabilities_from_task(B.task_description);M=B.task_description.lower().split();print(f"Extracted capabilities from task: {I}")
		J=set()
		if B.required_capabilities:J.update(A.lower()for A in B.required_capabilities)
		if I:J.update(A.lower()for A in I)
		A=[];A.append({'$lookup':{'from':_C,'localField':_D,'foreignField':_B,'as':_C}})
		if J:
			N=[]
			for U in J:N.append({H:[{'capabilities.name':{G:U,F:E}},{'capabilities.description':{G:U,F:E}}]})
			if N:A.append({S:{H:N}});A.append({R:{L:{'$sum':[{'$cond':[{'$eq':[Q,[]]},0,1]},{'$size':Q}]}}})
		if M:
			O=[]
			for P in M:
				if len(P)>3:O.append({H:[{_E:{G:P,F:E}},{'description':{G:P,F:E}}]})
			if O:A.append({S:{H:O}});A.append({R:{L:{'$add':['$score',1]}}})
		A.append({'$sort':{L:-1}});A.append({'$limit':B.top_n})
		if not A:V=K.agents_collection.find().limit(B.top_n)
		else:V=K.agents_collection.aggregate(A)
		async for C in V:
			if _A in C:del C[_A]
			W=[]
			for D in C.get(_C,[]):
				if _A in D:del D[_A]
				if _B in D:del D[_B]
				W.append(Capability(**D))
			C[_C]=W;T.append(RegisteredAgent(**C))
		return T
	async def update_agent_registration(C,registry_id,agent_update_data):
		'Update an existing agent registration';A=agent_update_data;B=registry_id;G=await C.get_agent_by_id(B)
		if not G:return
		A.id=B;A.updated_at=datetime.now();E=A.capabilities;H=A.dict(exclude={_C});await C.agents_collection.replace_one({_D:B},H);await C.capabilities_collection.delete_many({_B:B})
		if E:
			D=[]
			for I in E:F=I.dict();F[_B]=B;D.append(F)
			if D:await C.capabilities_collection.insert_many(D)
		return A
	async def delete_agent_registration(A,registry_id):'Delete an agent registration and its capabilities';B=registry_id;C=await A.agents_collection.delete_one({_D:B});await A.capabilities_collection.delete_many({_B:B});return C.deleted_count>0