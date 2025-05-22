_A='description'
from typing import Dict,Set
from app.db.schemas import UserInDBBase,ClientInDB
fake_users_db={}
fake_clients_db={}
fake_roles_db={'user':{_A:'Standard user'},'admin':{_A:'Administrator with all permissions'},'service':{_A:'Service account role'}}
fake_user_roles_db={}
fake_refresh_tokens_db={}
_user_id_counter=0
_client_id_counter=0
_role_id_counter=0
def get_next_user_id():global _user_id_counter;_user_id_counter+=1;return _user_id_counter
def get_next_client_id():global _client_id_counter;_client_id_counter+=1;return _client_id_counter
def get_next_role_id():global _role_id_counter;_role_id_counter+=1;return _role_id_counter