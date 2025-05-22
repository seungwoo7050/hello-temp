_B=None
_A=True
from pydantic import BaseModel,EmailStr,Field
from typing import Optional,List,Dict,Any
class Token(BaseModel):access_token:str;refresh_token:str;token_type:str
class TokenData(BaseModel):username:Optional[str]=_B;scopes:List[str]=[];sub:Optional[str]=_B
class UserBase(BaseModel):username:str=Field(...,min_length=3,max_length=50);email:Optional[EmailStr]=_B;full_name:Optional[str]=_B
class UserCreate(UserBase):password:str=Field(...,min_length=8)
class UserInDBBase(UserBase):
	id:int;hashed_password:str;is_active:bool=_A;roles:List[str]=[]
	class Config:from_attributes=_A
class User(UserInDBBase):0
class UserPublic(UserBase):
	id:int;is_active:bool=_A;roles:List[str]=[]
	class Config:from_attributes=_A
class ClientBase(BaseModel):client_id:str=Field(...,min_length=3,max_length=50);client_name:Optional[str]=_B
class ClientCreate(ClientBase):client_secret:str=Field(...,min_length=12);grant_types:List[str]=['client_credentials'];scopes:List[str]=[]
class ClientInDB(ClientBase):
	id:int;hashed_client_secret:str;grant_types:List[str];scopes:List[str];is_active:bool=_A
	class Config:from_attributes=_A
class ClientPublic(ClientBase):
	id:int;grant_types:List[str];scopes:List[str];is_active:bool=_A
	class Config:from_attributes=_A
class RoleCreate(BaseModel):name:str=Field(...,min_length=2,max_length=30);description:Optional[str]=_B
class Role(RoleCreate):
	id:int
	class Config:from_attributes=_A