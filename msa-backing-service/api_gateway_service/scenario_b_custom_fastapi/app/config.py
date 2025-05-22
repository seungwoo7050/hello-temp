_A=None
import yaml
from typing import List,Dict,Optional,Any
from pydantic import BaseModel,HttpUrl
import os
CONFIG_PATH=os.getenv('API_GW_CONFIG_PATH','app/routes.yml')
class RateLimitConfig(BaseModel):requests:int;per_seconds:int
class RouteConfig(BaseModel):path_prefix:str;target_base_url:HttpUrl;methods:List[str]=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'];host:Optional[str]=_A;strip_prefix:bool=True;requires_auth:bool=False;rate_limit:Optional[RateLimitConfig]=_A;add_headers:Optional[Dict[str,str]]=_A;transform_response_headers:Optional[Dict[str,str]]=_A
class GatewayConfig(BaseModel):routes:List[RouteConfig]
def load_config(path=CONFIG_PATH):
	try:
		with open(path,'r')as A:B=yaml.safe_load(A)
		return GatewayConfig(**B)
	except FileNotFoundError:print(f"Error: Configuration file not found at {path}");return GatewayConfig(routes=[])
	except Exception as C:print(f"Error loading or parsing configuration: {C}");return GatewayConfig(routes=[])
gateway_config=load_config()