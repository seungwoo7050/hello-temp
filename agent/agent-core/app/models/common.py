from pydantic import BaseModel
from typing import Optional,List,Dict,Any
class PyObjectId(str):
	@classmethod
	def __get_validators__(A):yield A.validate
	@classmethod
	def validate(A,v):
		if not isinstance(v,str)or not len(v)==24:0
		return v
	@classmethod
	def __modify_schema__(A,field_schema):field_schema.update(type='string')
class StatusMessage(BaseModel):message:str;details:Optional[str]=None
class Tool(BaseModel):type:str;name:str;description:Optional[str]=None;parameters:Optional[Dict[str,Any]]=None
class VertexAISettings(BaseModel):project_id:str;location:str;model_id:str='gemini-1.5-pro-latest'