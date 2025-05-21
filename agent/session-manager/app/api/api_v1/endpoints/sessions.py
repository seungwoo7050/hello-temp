from fastapi import APIRouter,Depends,HTTPException,Query,status,Body
from typing import List,Optional,Dict,Any
from app.schemas.session import Session,CreateSessionRequest,SendMessageRequest,SendMessageResponse,SessionDetailsResponse,SessionMemoryResponse,SessionMemory
from app.schemas.common import StatusMessage
from app.services.session_service import SessionService
from app.core.dependencies import get_session_service
router=APIRouter()
@router.post('/',response_model=SessionDetailsResponse,status_code=status.HTTP_201_CREATED,summary='Create New Session')
async def create_session(request,session_service=Depends(get_session_service)):
	'\n    Create a new session for interacting with a specific agent.\n    Optionally, an initial message can be provided to start the conversation.\n    '
	try:B=await session_service.create_session(request);return SessionDetailsResponse(**B.dict())
	except ValueError as A:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to create session: {str(A)}")
@router.get('/',response_model=List[SessionDetailsResponse],summary='List Sessions')
async def list_sessions(user_id=Query(None,description='Filter sessions by user ID.'),agent_id=Query(None,description='Filter sessions by agent ID.'),skip=Query(0,ge=0),limit=Query(100,ge=1,le=200),session_service=Depends(get_session_service)):
	'\n    Retrieve a list of sessions, optionally filtered by user ID or agent ID.\n    '
	try:A=await session_service.list_sessions(user_id=user_id,agent_id=agent_id,skip=skip,limit=limit);return[SessionDetailsResponse(**A.dict())for A in A]
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to list sessions: {str(B)}")
@router.get('/{session_id}',response_model=SessionDetailsResponse,summary='Get Session Details')
async def get_session_details(session_id,session_service=Depends(get_session_service)):
	'\n    Get detailed information about a specific session by its ID.\n    ';A=session_id;B=await session_service.get_session(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Session with ID '{A}' not found.")
	return SessionDetailsResponse(**B.dict())
@router.post('/{session_id}/messages',response_model=SendMessageResponse,summary='Send Message to Session')
async def send_message_to_session(session_id,message_request,session_service=Depends(get_session_service)):
	"\n    Send a message from a user to the agent associated with the session.\n    Returns the agent's reply.\n    ";B=session_id
	try:
		C=await session_service.send_message_to_agent(B,message_request)
		if not C:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Session '{B}' not found or failed to process message.")
		return C
	except ValueError as A:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to send message in session {B}: {str(A)}")
@router.get('/{session_id}/memory',response_model=SessionMemoryResponse,summary='Get Session Memory')
async def get_session_memory(session_id,session_service=Depends(get_session_service)):
	'\n    Retrieve the current memory state (short-term history, etc.) for a specific session.\n    ';A=session_id;B=await session_service.get_session_memory(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Memory for session '{A}' not found (session may not exist).")
	return SessionMemoryResponse(**B.dict())
@router.post('/{session_id}/close',response_model=SessionDetailsResponse,summary='Close Session')
async def close_session(session_id,session_service=Depends(get_session_service)):
	'\n    Mark a session as closed. Further interactions may be disallowed.\n    ';A=session_id;B=await session_service.close_session(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Session '{A}' not found or already closed/invalid.")
	return SessionDetailsResponse(**B.dict())