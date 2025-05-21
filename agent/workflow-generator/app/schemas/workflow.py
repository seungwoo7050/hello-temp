_A=None
from pydantic import BaseModel,Field
from typing import Optional,List,Dict,Any
from datetime import datetime
import uuid
from app.schemas.task import SubTask
from app.schemas.common import ToolDefinition,LLMConfig
class WorkflowNode(BaseModel):id:str;node_type:str;content:Dict[str,Any]
class WorkflowEdge(BaseModel):source_node_id:str;target_node_id:str;condition:Optional[str]=_A
class WorkflowGraph(BaseModel):nodes:List[WorkflowNode];edges:List[WorkflowEdge];entry_point:str
class WorkflowDefinition(BaseModel):name:str;description:Optional[str]=_A;task_description_template:Optional[str]=_A;graph:WorkflowGraph;required_tools:List[ToolDefinition]=[];llm_config:Optional[LLMConfig]=_A;output_schema:Optional[Dict[str,Any]]=_A
class WorkflowCreateRequest(BaseModel):task_description:str;name:Optional[str]=_A;description:Optional[str]=_A
class Workflow(BaseModel):id:str=Field(default_factory=lambda:f"wf_{uuid.uuid4().hex}");name:str;description:Optional[str]=_A;definition:WorkflowDefinition;created_at:datetime=Field(default_factory=datetime.now);updated_at:datetime=Field(default_factory=datetime.now);version:int=1;agent_representation:Optional[Dict[str,Any]]=_A
class WorkflowExecutionRequest(BaseModel):input_data:Dict[str,Any]
class WorkflowExecutionResponse(BaseModel):workflow_id:str;status:str;result:Optional[Dict[str,Any]]=_A;error_message:Optional[str]=_A;execution_log:List[str]=[]
class WorkflowRegistrationRequest(BaseModel):agent_name:str;agent_description:Optional[str]=_A