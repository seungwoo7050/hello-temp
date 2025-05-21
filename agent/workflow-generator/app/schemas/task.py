from pydantic import BaseModel,Field
from typing import Optional,List,Dict,Any
class TaskDecompositionRequest(BaseModel):task_description:str
class SubTask(BaseModel):id:str=Field(default_factory=lambda:f"subtask_{uuid.uuid4().hex[:8]}");description:str;assigned_agent_type:Optional[str]=None;required_tools:List[str]=[];depends_on:List[str]=[];parameters:Dict[str,Any]={}
class TaskDecompositionResponse(BaseModel):original_task:str;sub_tasks:List[SubTask];execution_graph_hint:Optional[Dict[str,Any]]=None