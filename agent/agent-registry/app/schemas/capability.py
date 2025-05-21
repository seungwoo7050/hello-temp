_A=None
from pydantic import BaseModel,Field
from typing import List,Optional,Dict,Any
from datetime import datetime
import uuid
class AgentTool(BaseModel):name:str;description:Optional[str]=_A;type:str='function';specification:Optional[Dict[str,Any]]=_A
class Capability(BaseModel):name:str;description:str;input_schema:Optional[Dict[str,Any]]=_A;output_schema:Optional[Dict[str,Any]]=_A;associated_tools:List[AgentTool]=[]
class RegisteredAgent(BaseModel):id:str=Field(default_factory=lambda:f"reg-agent-{uuid.uuid4().hex}");agent_id_external:str;name:str;description:Optional[str]=_A;capabilities:List[Capability]=[];endpoint:Optional[str]=_A;source:str='unknown';registered_at:datetime=Field(default_factory=datetime.now);updated_at:datetime=Field(default_factory=datetime.now);metadata:Optional[Dict[str,Any]]=_A
class AgentCapabilityInput(BaseModel):agent_id_external:str;name:str;description:Optional[str]=_A;capabilities:List[Capability];endpoint:Optional[str]=_A;source:Optional[str]='manual';metadata:Optional[Dict[str,Any]]=_A
class CapabilityMatchRequest(BaseModel):task_description:Optional[str]=_A;required_capabilities:Optional[List[str]]=_A;top_n:int=Query(5,ge=1,le=20)
class CapabilityMatchResponse(BaseModel):query:CapabilityMatchRequest;matched_agents:List[RegisteredAgent]