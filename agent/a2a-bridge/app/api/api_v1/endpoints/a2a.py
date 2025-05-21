_B='/interactions'
_A=None
from fastapi import APIRouter,Depends,HTTPException,Query,status,Body,Path,Header
from typing import List,Optional,Dict,Any
from app.schemas.a2a import InitiateInteractionRequest,InitiateInteractionResponse,SendA2AMessageRequest,SendA2AMessageResponse,A2AMessage,Interaction,DiscoveredAgent
from app.schemas.common import StatusMessage
from app.services.a2a_bridge_service import A2ABridgeService
from app.core.dependencies import get_a2a_bridge_service,get_current_agent_id
from app.core.security import verify_agent_token
router=APIRouter()
@router.post(_B,response_model=InitiateInteractionResponse,status_code=status.HTTP_201_CREATED,summary='Initiate A2A Interaction')
async def initiate_a2a_interaction(request,a2a_service=Depends(get_a2a_bridge_service)):
	'\n    Initiate a new communication interaction between two agents.\n    This will set up the necessary context and potentially send an initial message if provided.\n    '
	try:B=await a2a_service.initiate_interaction(request);return B
	except ValueError as A:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to initiate A2A interaction: {str(A)}")
@router.get(_B,response_model=List[Interaction],summary='List A2A Interactions')
async def list_a2a_interactions(agent_id=Query(_A,description='Filter interactions involving this agent ID.'),status=Query(_A,description='Filter interactions by status (e.g., active, completed).'),skip=Query(0,ge=0),limit=Query(100,ge=1,le=200),a2a_service=Depends(get_a2a_bridge_service)):
	'\n    Retrieve a list of A2A interactions, optionally filtered by participating agent ID or status.\n    ';A=status
	try:B=await a2a_service.list_interactions(agent_id=agent_id,status=A,skip=skip,limit=limit);return B
	except Exception as C:raise HTTPException(status_code=A.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to list A2A interactions: {str(C)}")
@router.get('/interactions/{interaction_id}',response_model=Interaction,summary='Get A2A Interaction Details')
async def get_a2a_interaction_details(interaction_id=Path(...,description='The ID of the A2A interaction to retrieve.'),a2a_service=Depends(get_a2a_bridge_service)):
	'\n    Get detailed information about a specific A2A interaction, including message history.\n    ';A=interaction_id;B=await a2a_service.get_interaction_details(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"A2A Interaction with ID '{A}' not found.")
	return B
@router.post('/interactions/{interaction_id}/messages',response_model=SendA2AMessageResponse,summary='Send Message in A2A Interaction')
async def send_message_in_a2a_interaction(message_request,interaction_id=Path(...,description='The ID of the ongoing A2A interaction.'),x_agent_id=Header(_A,description='ID of the source agent sending the message'),authorization=Header(_A,description='Agent authorization token'),a2a_service=Depends(get_a2a_bridge_service)):
	'\n    Send a message from one agent to another within an existing A2A interaction.\n    \n    The source agent ID can be provided in several ways (in order of precedence):\n    1. In the message_request.source_agent_id field\n    2. Through the X-Agent-ID header\n    3. Extracted from the authorization token\n    ';J='agent_id';H=a2a_service;G=authorization;F=x_agent_id;D=message_request;C=interaction_id;E=await H.get_interaction_details(C)
	if not E or not E.primary_agent_ids:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Interaction '{C}' not found or has no primary agents defined.")
	A=_A
	if hasattr(D,'source_agent_id')and D.source_agent_id:A=D.source_agent_id
	elif F:A=F
	elif G:
		try:
			I=verify_agent_token(G)
			if J in I:A=I[J]
		except Exception as B:pass
	if not A:A=E.primary_agent_ids[0]
	if A not in E.primary_agent_ids:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Agent '{A}' is not a participant in interaction '{C}'.")
	try:K=await H.route_message(interaction_id=C,source_agent_id=A,message_request=D);return K
	except ValueError as B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(B))
	except ConnectionError as B:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(B))
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to send message in A2A interaction {C}: {str(B)}")
@router.get('/discover-agents',response_model=List[DiscoveredAgent],summary='Discover A2A Capable Agents')
async def discover_a2a_capable_agents(a2a_service=Depends(get_a2a_bridge_service)):
	'\n    Discover agents that are available and capable of A2A communication.\n    (This typically proxies a request to the Agent Registry service).\n    '
	try:A=await a2a_service.discover_a2a_agents();return A
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to discover A2A agents: {str(B)}")