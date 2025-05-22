from fastapi import APIRouter,Depends,HTTPException,status,Form
from typing import List
from app.db import schemas,crud
from app.core import security,config
from datetime import timedelta
router=APIRouter()
@router.post('/token',response_model=schemas.Token)
async def client_credentials_token(grant_type=Form(...),client_id=Form(...),client_secret=Form(...)):
	'\n    OAuth 2.0 Client Credentials Grant.\n    Used for M2M (machine-to-machine) authentication.\n    ';D='Basic';C='WWW-Authenticate';B='client_credentials'
	if grant_type!=B:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Unsupported grant type')
	A=crud.get_client_by_client_id(client_id)
	if not A:raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid client_id',headers={C:D})
	if not security.verify_password(client_secret,A.hashed_client_secret):raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid client_secret',headers={C:D})
	if not A.is_active:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Inactive client')
	if B not in A.grant_types:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Grant type not allowed for this client')
	E=timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES);F=security.create_access_token(data={'sub':A.client_id,'scopes':A.scopes,'type':'client_access'},expires_delta=E);return{'access_token':F,'refresh_token':'','token_type':'bearer'}
from app.core.dependencies import require_role
@router.post('/clients',response_model=schemas.ClientPublic,status_code=status.HTTP_201_CREATED,dependencies=[Depends(require_role('admin'))])
async def register_new_client(client_in):
	'\n    Register a new API client (Admin only).\n    ';A=client_in;C=crud.get_client_by_client_id(client_id=A.client_id)
	if C:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Client ID already registered')
	B=crud.create_client(client_in=A)
	if not B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Could not create client')
	return schemas.ClientPublic.model_validate(B)
@router.get('/clients/{client_id_param}',response_model=schemas.ClientPublic,dependencies=[Depends(require_role('admin'))])
async def read_client_info(client_id_param):
	'\n    Get client information by client_id (Admin only).\n    ';A=crud.get_client_by_client_id(client_id_param)
	if A is None:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Client not found')
	return schemas.ClientPublic.model_validate(A)