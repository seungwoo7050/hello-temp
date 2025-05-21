_C='active'
_B='user'
_A=None
from pydantic import BaseModel,Field
from typing import List,Optional,Dict,Any,Literal
from datetime import datetime
import uuid
class Message(BaseModel):role:Literal[_B,'agent','system'];content:str;timestamp:datetime=Field(default_factory=datetime.now);metadata:Optional[Dict[str,Any]]=_A
class ShortTermMemory(BaseModel):
	messages:List[Message]=[];max_history_length:int=20
	def add_message(A,message):
		A.messages.append(message)
		if len(A.messages)>A.max_history_length:A.messages=A.messages[-A.max_history_length:]
class LongTermMemoryConfig(BaseModel):type:str='vector_store';config:Dict[str,Any]={}
class SessionMemory(BaseModel):short_term:ShortTermMemory=Field(default_factory=ShortTermMemory)
class Session(BaseModel):id:str=Field(default_factory=lambda:f"sess-{uuid.uuid4().hex}");agent_id:str;user_id:Optional[str]=_A;vertex_session_id:Optional[str]=_A;created_at:datetime=Field(default_factory=datetime.now);last_accessed_at:datetime=Field(default_factory=datetime.now);status:Literal[_C,'expired','closed']=_C;memory:SessionMemory=Field(default_factory=SessionMemory);metadata:Optional[Dict[str,Any]]=_A
class CreateSessionRequest(BaseModel):agent_id:str;user_id:Optional[str]=_A;initial_message:Optional[Message]=_A;metadata:Optional[Dict[str,Any]]=_A
class SendMessageRequest(BaseModel):message_content:str;role:Literal[_B]=_B
class SendMessageResponse(BaseModel):session_id:str;user_message:Message;agent_reply:Message;updated_memory:Optional[SessionMemory]=_A
class SessionDetailsResponse(Session):0
class SessionMemoryResponse(SessionMemory):0