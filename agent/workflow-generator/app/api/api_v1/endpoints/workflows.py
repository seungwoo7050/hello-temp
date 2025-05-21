from fastapi import APIRouter,Depends,HTTPException,Query,status,Body
from typing import List,Optional,Dict,Any
from app.schemas.workflow import WorkflowCreateRequest,Workflow,WorkflowExecutionRequest,WorkflowExecutionResponse,WorkflowRegistrationRequest
from app.schemas.common import StatusMessage
from app.services.workflow_service import WorkflowService
from app.core.dependencies import get_workflow_service
router=APIRouter()
@router.post('/',response_model=Workflow,status_code=status.HTTP_201_CREATED,summary='Create Dynamic Workflow')
async def create_workflow(request,workflow_service=Depends(get_workflow_service)):
	'\n    Generate and store a new dynamic workflow based on a task description.\n    '
	try:B=await workflow_service.create_workflow(request);return B
	except ValueError as A:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to create workflow: {str(A)}")
@router.get('/',response_model=List[Workflow],summary='List All Workflows')
async def list_workflows(skip=Query(0,ge=0),limit=Query(100,ge=1,le=200),workflow_service=Depends(get_workflow_service)):
	'\n    Retrieve a list of all stored workflows.\n    '
	try:A=await workflow_service.list_workflows(skip=skip,limit=limit);return A
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to list workflows: {str(B)}")
@router.get('/{workflow_id}',response_model=Workflow,summary='Get Workflow Details')
async def get_workflow(workflow_id,workflow_service=Depends(get_workflow_service)):
	'\n    Get detailed information about a specific workflow by its ID.\n    ';A=workflow_id;B=await workflow_service.get_workflow(A)
	if not B:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Workflow with ID '{A}' not found.")
	return B
@router.post('/{workflow_id}/execute',response_model=WorkflowExecutionResponse,summary='Execute Workflow')
async def execute_workflow(workflow_id,exec_request,workflow_service=Depends(get_workflow_service)):
	'\n    Execute a stored workflow with the given input data.\n    ';C=workflow_id
	try:
		A=await workflow_service.execute_workflow(C,exec_request)
		if A.status=='NOT_FOUND':raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=A.error_message)
		return A
	except ValueError as B:raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(B))
	except Exception as B:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to execute workflow {C}: {str(B)}")
@router.post('/{workflow_id}/register',response_model=Dict[str,Any],summary='Register Workflow as Agent')
async def register_workflow_as_agent(workflow_id,registration_details=Body(None),workflow_service=Depends(get_workflow_service)):
	'\n    Register an existing workflow as a new reusable agent in the Agent Core service.\n    ';B=registration_details;C=workflow_id
	try:D=B.dict()if B else{};E=await workflow_service.register_workflow_as_agent(C,D);return E
	except ValueError as A:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(A))
	except ConnectionError as A:raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(A))
	except Exception as A:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Failed to register workflow {C} as agent: {str(A)}")