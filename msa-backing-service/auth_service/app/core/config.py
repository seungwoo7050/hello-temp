import os
from dotenv import load_dotenv
from typing import List
load_dotenv()
class Settings:PROJECT_NAME:str='Auth Service';PROJECT_VERSION:str='0.1.0';SECRET_KEY:str=os.getenv('SECRET_KEY','default_secret_key_please_change');ALGORITHM:str=os.getenv('ALGORITHM','HS256');ACCESS_TOKEN_EXPIRE_MINUTES:int=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES',30));REFRESH_TOKEN_EXPIRE_DAYS:int=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS',7));INITIAL_ADMIN_USERNAME:str=os.getenv('INITIAL_ADMIN_USERNAME','admin');INITIAL_ADMIN_PASSWORD:str=os.getenv('INITIAL_ADMIN_PASSWORD','supersecret');INITIAL_ADMIN_EMAIL:str=os.getenv('INITIAL_ADMIN_EMAIL','admin@example.com');ALLOWED_ORIGINS:List[str]=['http://localhost','http://localhost:8080']
settings=Settings()