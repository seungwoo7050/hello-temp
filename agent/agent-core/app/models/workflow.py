from pydantic import BaseModel
from typing import Optional
class WorkflowConversionRequest(BaseModel):workflow_id:str;name:str;description:Optional[str]=None