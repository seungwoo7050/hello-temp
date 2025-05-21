from pydantic import BaseModel
from typing import Optional,List,Dict,Any
from datetime import datetime
class StatusMessage(BaseModel):message:str;details:Optional[str]=None
class ToolParameter(BaseModel):name:str;type:str;description:Optional[str]=None;required:bool=False
class ToolDefinition(BaseModel):name:str;description:str;parameters:List[ToolParameter]=[]
class LLMConfig(BaseModel):model_id:str='gemini-1.5-pro-latest';temperature:float=.7;max_output_tokens:int=1024