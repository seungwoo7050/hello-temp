_A=None
from pydantic import BaseModel,Field
from typing import List,Optional,Dict,Any,Literal
from datetime import datetime
import uuid
class A2AMessageContent(BaseModel):type:str='text';payload:Any
class A2AMessage(BaseModel):id:str=Field(default_factory=lambda:f"a2a-msg-{uuid.uuid4().hex}");interaction_id:str;source_agent_id:str;target_agent_id:str;content:A2AMessageContent;timestamp:datetime=Field(default_factory=datetime.now);protocol_metadata:Optional[Dict[str,Any]]=_A
class Interaction(BaseModel):id:str=Field(default_factory=lambda:f"a2a-interaction-{uuid.uuid4().hex}");primary_agent_ids:List[str];goal_description:Optional[str]=_A;status:str='pending';user_id:Optional[str]=_A;agent_session_map:Dict[str,str]=Field(default_factory=dict);message_history:List[A2AMessage]=[];created_at:datetime=Field(default_factory=datetime.now);updated_at:datetime=Field(default_factory=datetime.now);metadata:Optional[Dict[str,Any]]=_A
class InitiateInteractionRequest(BaseModel):source_agent_id:str;target_agent_id:str;goal:str;user_id:Optional[str]=_A;initial_message_content:Optional[A2AMessageContent]=_A
class InitiateInteractionResponse(BaseModel):interaction:Interaction;initial_message_sent:Optional[A2AMessage]=_A
class SendA2AMessageRequest(BaseModel):content:A2AMessageContent
class SendA2AMessageResponse(BaseModel):message_sent:A2AMessage
class DiscoveredAgent(BaseModel):agent_id:str;name:str;description:Optional[str]=_A;capabilities:List[str]