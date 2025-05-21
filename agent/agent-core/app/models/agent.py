_D='2025-05-21T10:00:00Z'
_C='description'
_B='gemini-1.5-pro-latest'
_A=None
from pydantic import BaseModel,Field
from typing import List,Optional,Dict,Any
from datetime import datetime
from.common import PyObjectId,Tool
class AgentBase(BaseModel):name:str;description:Optional[str]=_A;instructions:Optional[str]=_A;model_id:Optional[str]=_B;tools:Optional[List[Tool]]=[];metadata:Optional[Dict[str,Any]]=_A
class AgentCreate(AgentBase):0
class AgentUpdate(AgentBase):name:Optional[str]=_A
class Agent(AgentBase):
	id:str=Field(...,alias='_id');status:str='CREATED';created_at:datetime=Field(default_factory=datetime.now);updated_at:datetime=Field(default_factory=datetime.now);deployment_info:Optional[Dict[str,Any]]=_A
	class Config:json_encoders={datetime:lambda dt:dt.isoformat()};allow_population_by_field_name=True;schema_extra={'example':{'name':'Customer Service Agent',_C:'Handles customer inquiries and support tickets.','instructions':'You are a helpful customer service agent...','model_id':_B,'tools':[{'type':'function','name':'get_order_status',_C:'Retrieves the status of an order'}],'status':'ACTIVE','created_at':_D,'updated_at':_D,'deployment_info':{'endpoint':'projects/.../endpoints/...'}}}
class AgentDefinition(BaseModel):name:str;description:Optional[str]=_A;model:str;instructions:str;tools:Optional[List[Tool]]=[];serialized_graph:Optional[Dict[str,Any]]=_A
class AgentDeploymentResponse(BaseModel):agent_id:str;status:str;message:Optional[str]=_A;deployment_details:Optional[Dict[str,Any]]=_A