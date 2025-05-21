from pydantic import BaseModel
from typing import Optional
class StatusMessage(BaseModel):message:str;details:Optional[str]=None