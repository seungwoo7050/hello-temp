_A='/{registry_id}'
from fastapi import APIRouter,Depends,HTTPException,Query,status,Body
from typing import List,Optional,Dict,Any
from app.schemas.capability import RegisteredAgent,AgentCapabilityInput,CapabilityMatchRequest,CapabilityMatchResponse
from app.schemas.common import StatusMessage
from app.services.registry_service import AgentRegistryService
from app.core.dependencies import get_registry_service
router=APIRouter()
@router.post('/',response_model=RegisteredAgent,status_code=status.HTTP_201_CREATED,summary='Register Agent Capability')
async def register_agent_capability(agent_input,registry_service=Depends(get_registry_service)):
	'\n    Register a new agent and its capabilities in the registry.\n    If an agent with the same external ID already exists, its information will be updated.\n    '
	try:B=await registry_service.register_agent_capability(agent_input);return B
	except ValueError as A:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to register agent capability: {str(A)}")
@router.get('/',response_model=List[RegisteredAgent],summary='List Registered Agents')
async def list_registered_agents(skip=Query(0,ge=0),limit=Query(100,ge=1,le=200),registry_service=Depends(get_registry_service)):
	'\n    Retrieve a list of all agents registered in the capability registry.\n    '
	try:A=await registry_service.list_registered_agents(skip=skip,limit=limit);return A
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to list registered agents: {str(B)}")
@router.get('/match',response_model=CapabilityMatchResponse,summary='Find Matching Agents for a Task/Capability')
async def find_matching_agents(task_description=Query(None,description='Natural language description of the task.'),required_capabilities=Query(None,description='List of specific capability names required.'),top_n=Query(5,ge=1,le=20,description='Number of top matching agents to return.'),registry_service=Depends(get_registry_service)):
	'\n    Find agents that match a given task description or a list of required capabilities.\n    - If `task_description` is provided, the service might use it to infer capabilities.\n    - If `required_capabilities` are provided, agents possessing all of them will be matched.\n    - Both can be used together for a more refined search.\n    ';A=required_capabilities;B=task_description
	if not B and not A:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Either 'task_description' or 'required_capabilities' must be provided for matching.")
	C=CapabilityMatchRequest(task_description=B,required_capabilities=A,top_n=top_n)
	try:D=await registry_service.find_agents_for_task(C);return D
	except Exception as E:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to find matching agents: {str(E)}")
@router.get(_A,response_model=RegisteredAgent,summary='Get Registered Agent Details')
async def get_registered_agent_details(registry_id,registry_service=Depends(get_registry_service)):
	'\n    Get detailed information about a specific agent registered in the capability registry by its internal registry ID.\n    ';A=registry_id;B=await registry_service.get_registered_agent(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Agent with registry ID '{A}' not found.")
	return B
@router.delete(_A,response_model=StatusMessage,summary='Delete Agent Registration')
async def delete_agent_registration(registry_id,registry_service=Depends(get_registry_service)):
	"\n    Delete an agent's registration from the capability registry using its internal registry ID.\n    This does not delete the agent from Agent Core or Vertex AI.\n    ";A=registry_id;B=await registry_service.delete_agent_registration(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Agent with registry ID '{A}' not found or could not be deleted.")
	return StatusMessage(message=f"Agent registration '{A}' deleted successfully.")