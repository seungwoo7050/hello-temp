_U='parameters'
_T='original_task_description'
_S='task_description'
_R='error'
_Q='...'
_P='processing_node'
_O='tool_node'
_N='output'
_M='llm_node'
_L='started'
_K=None
_J='completed'
_I='current_sub_task_id'
_H='failed'
_G='error_message'
_F='execution_log'
_E='status'
_D='node_type'
_C='node_id'
_B='timestamp'
_A='sub_task_outputs'
from langgraph.graph import StateGraph,END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolExecutor
from app.schemas.workflow import WorkflowGraph,WorkflowNode,WorkflowEdge,WorkflowDefinition
from app.schemas.task import SubTask,TaskDecompositionResponse
from app.core.config import settings
from typing import TypedDict,Annotated,List,Dict,Any,Callable,Union,Optional
import operator,uuid,json,asyncio
from datetime import datetime
from pydantic import BaseModel
class DynamicWorkflowState(TypedDict):original_task_description:str;current_sub_task_id:str;sub_task_outputs:Dict[str,Any];final_result:Any;error_message:Annotated[str,operator.setitem];execution_log:List[Dict[str,Any]];execution_start_time:str;execution_status:str
class WorkflowExecutionResponse(BaseModel):workflow_id:str;execution_id:str;status:str;result:Optional[Dict[str,Any]]=_K;logs:List[Dict[str,Any]]=[];error:Optional[str]=_K;execution_time:Optional[float]=_K
async def execute_llm_node(state,node_config):
	'Execute an LLM-based node that generates content';from vertexai.generative_models import GenerativeModel,GenerationConfig;sub_task_id=node_config.id;node_content=node_config.content;prompt_template=node_content.get('prompt_template','No prompt provided');model_id=node_content.get('model_id',settings.DEFAULT_LLM_MODEL_ID);log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_M,_E:_L,'input':prompt_template};new_state=state.copy();execution_log=new_state.get(_F,[]);execution_log.append(log_entry);new_state[_F]=execution_log
	try:
		previous_outputs=state.get(_A,{});input_vars={_S:state.get(_T,''),**previous_outputs};formatted_prompt=prompt_template
		for(var_name,var_value)in input_vars.items():
			if isinstance(var_value,str):formatted_prompt=formatted_prompt.replace(f"{{{{{var_name}}}}}",var_value)
		model=GenerativeModel(model_id);response=await model.generate_content_async(formatted_prompt,generation_config=GenerationConfig(temperature=node_content.get('temperature',.7),max_output_tokens=node_content.get('max_tokens',1024),top_p=node_content.get('top_p',.95)))
		if response.candidates and response.candidates[0].content.parts:output_text=response.candidates[0].content.parts[0].text
		else:output_text='No output generated from LLM'
		current_outputs=state.get(_A,{});current_outputs[sub_task_id]=output_text;new_state[_A]=current_outputs;new_state[_I]=sub_task_id;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_M,_E:_J,_N:output_text[:100]+(_Q if len(output_text)>100 else'')};execution_log.append(log_entry);return new_state
	except Exception as e:error_msg=f"Error in LLM node {sub_task_id}: {str(e)}";new_state[_G]=error_msg;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_M,_E:_H,_R:str(e)};execution_log.append(log_entry);return new_state
async def execute_tool_node(state,node_config):
	'Execute a node that calls an external tool';A='name';sub_task_id=node_config.id;node_content=node_config.content;tool_name=node_content.get('tool_name','unknown_tool');input_mapping=node_content.get('input_mapping',{});log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_O,_E:_L,'tool':tool_name};new_state=state.copy();execution_log=new_state.get(_F,[]);execution_log.append(log_entry);new_state[_F]=execution_log
	try:
		previous_outputs=state.get(_A,{});tool_inputs={}
		for(param_name,input_template)in input_mapping.items():
			if isinstance(input_template,str)and'{{'in input_template and'}}'in input_template:
				formatted_input=input_template
				for(var_name,var_value)in previous_outputs.items():
					if isinstance(var_value,str):formatted_input=formatted_input.replace(f"{{{{{var_name}}}}}",var_value)
				tool_inputs[param_name]=formatted_input
			else:tool_inputs[param_name]=input_template
		tool_config={A:tool_name,'description':f"Tool {tool_name} for {sub_task_id}",_U:tool_inputs};tool_executor=ToolExecutor(tools=[tool_config]);tool_result=await tool_executor.ainvoke({A:tool_name,**tool_inputs});current_outputs=state.get(_A,{});current_outputs[sub_task_id]=tool_result;new_state[_A]=current_outputs;new_state[_I]=sub_task_id;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_O,_E:_J,_N:str(tool_result)[:100]+_Q if len(str(tool_result))>100 else str(tool_result)};execution_log.append(log_entry);return new_state
	except Exception as e:error_msg=f"Error in tool node {sub_task_id}: {str(e)}";new_state[_G]=error_msg;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_O,_E:_H,_R:str(e)};execution_log.append(log_entry);return new_state
async def execute_processing_node(state,node_config):
	'Execute a node that performs data processing operations';D='transform_function';C='aggregate_field';B='count';A='operations';sub_task_id=node_config.id;node_content=node_config.content;operations=node_content.get(A,[]);parameters=node_content.get(_U,{});log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_P,_E:_L,A:operations};new_state=state.copy();execution_log=new_state.get(_F,[]);execution_log.append(log_entry);new_state[_F]=execution_log
	try:
		previous_outputs=state.get(_A,{});input_data=parameters.get('input_source');data_to_process=previous_outputs.get(input_data)if input_data else parameters.get('input_data');result=data_to_process
		for operation in operations:
			if operation=='filter'and isinstance(result,list):
				filter_key=parameters.get('filter_key','')
				if filter_key:result=[item for item in result if eval(f"item.{filter_key}")]
			elif operation=='aggregate'and isinstance(result,list):
				agg_type=parameters.get('aggregate_type',B)
				if agg_type==B:result=len(result)
				elif agg_type=='sum'and parameters.get(C):field=parameters.get(C);result=sum(item.get(field,0)for item in result)
			elif operation=='transform'and parameters.get(D):transform_code=parameters.get(D);transform_fn=eval(transform_code);result=transform_fn(result)
		current_outputs=state.get(_A,{});current_outputs[sub_task_id]=result;new_state[_A]=current_outputs;new_state[_I]=sub_task_id;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_P,_E:_J,_N:str(result)[:100]+_Q if len(str(result))>100 else str(result)};execution_log.append(log_entry);return new_state
	except Exception as e:error_msg=f"Error in processing node {sub_task_id}: {str(e)}";new_state[_G]=error_msg;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:_P,_E:_H,_R:str(e)};execution_log.append(log_entry);return new_state
async def execute_generic_task_node(state,node_config):'Default execution function for generic nodes';B='generic_node';A='instruction';sub_task_id=node_config.id;node_content=node_config.content;instruction=node_content.get(A,'No instruction provided.');log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:B,_E:_L,A:instruction};new_state=state.copy();execution_log=new_state.get(_F,[]);execution_log.append(log_entry);new_state[_F]=execution_log;print(f"LangGraph Node '{sub_task_id}': Executing with instruction: '{instruction}'");print(f"LangGraph Node '{sub_task_id}': Current state inputs: {state.get(_A)}");previous_outputs=state.get(_A,{});input_for_this_node=f"Context: {state.get(_T)}. Instruction: {instruction}. Previous relevant outputs: {previous_outputs}";mock_output=f"Output from node {sub_task_id} processing: {instruction[:30]}...";current_outputs=state.get(_A,{});current_outputs[sub_task_id]=mock_output;new_state[_A]=current_outputs;new_state[_I]=sub_task_id;log_entry={_B:datetime.now().isoformat(),_C:sub_task_id,_D:B,_E:_J,_N:mock_output};execution_log.append(log_entry);print(f"LangGraph Node '{sub_task_id}': Output: {mock_output}");return new_state
class LangGraphService:
	def __init__(self):
		if settings.LANGGRAPH_CHECKPOINT_TYPE=='sqlite'and settings.LANGGRAPH_SQLITE_PATH:self.checkpoint_db=SqliteSaver.from_conn_string(settings.LANGGRAPH_SQLITE_PATH);print(f"LangGraphService initialized with SQLite checkpoint: {settings.LANGGRAPH_SQLITE_PATH}")
		elif settings.LANGGRAPH_CHECKPOINT_TYPE=='vertex_ai':
			try:from langgraph.checkpoint.vertex import VertexAISaver;self.checkpoint_db=VertexAISaver(project_id=settings.VERTEX_AI_PROJECT_ID,location=settings.VERTEX_AI_LOCATION);print(f"LangGraphService initialized with Vertex AI checkpoint in {settings.VERTEX_AI_LOCATION}")
			except ImportError:print('Warning: VertexAISaver requested but not available. Falling back to MemorySaver.');self.checkpoint_db=MemorySaver()
		elif settings.LANGGRAPH_CHECKPOINT_TYPE=='firestore':
			try:from langgraph.checkpoint.firestore import FirestoreSaver;self.checkpoint_db=FirestoreSaver(collection_name=settings.FIRESTORE_COLLECTION,project_id=settings.GCP_PROJECT_ID);print(f"LangGraphService initialized with Firestore checkpoint")
			except ImportError:print('Warning: FirestoreSaver requested but not available. Falling back to MemorySaver.');self.checkpoint_db=MemorySaver()
		else:self.checkpoint_db=MemorySaver();print('LangGraphService initialized with In-Memory checkpoint.')
	def _create_node_function(self,node_config):
		'\n        Create and return a LangGraph node function based on node configuration.\n        Maps node types to their implementation functions.\n        ';A='generic';node_type=node_config.node_type.lower()if node_config.node_type else A;node_functions={_M:execute_llm_node,_O:execute_tool_node,_P:execute_processing_node,A:execute_generic_task_node};node_function=node_functions.get(node_type,execute_generic_task_node)
		async def node_function_wrapper(state):return await node_function(state,node_config)
		return node_function_wrapper
	def _create_conditional_edge(self,edge):
		'Create a conditional edge function based on edge configuration';condition=edge.condition
		def conditional_router(state):
			if not condition:return edge.target_node_id
			if condition.startswith('state.'):
				path=condition[6:].split('.');value=state
				for key in path:
					if isinstance(value,dict)and key in value:value=value[key]
					else:return
				if value:return edge.target_node_id
				return
			elif' == 'in condition or' != 'in condition or' > 'in condition or' < 'in condition:
				try:
					eval_condition=condition
					for(key,value)in state.items():
						if isinstance(value,(str,int,float,bool)):eval_condition=eval_condition.replace(f"state['{key}']",str(value));eval_condition=eval_condition.replace(f'state["{key}"]',str(value))
					if eval(eval_condition):return edge.target_node_id
					return
				except Exception as e:print(f"Error evaluating condition '{condition}': {e}");return
		return conditional_router
	def _determine_next_node(self,state,graph_edges):
		'\n        Enhanced router logic to determine the next node based on current state and edges.\n        Supports conditional routing and default paths.\n        ';current_node_id=state.get(_I)
		if not current_node_id:return'entry_point_placeholder'
		if state.get(_G):print(f"LangGraph Router: Error detected, routing to END");return END
		outgoing_edges=[edge for edge in graph_edges if edge.source_node_id==current_node_id]
		if not outgoing_edges:print(f"LangGraph Router: No further nodes from '{current_node_id}', routing to END.");return END
		for edge in outgoing_edges:
			if edge.condition:
				try:
					condition_met=self._create_conditional_edge(edge)(state)
					if condition_met:print(f"LangGraph Router: Condition met for edge from '{current_node_id}' to '{edge.target_node_id}' with condition '{edge.condition}'");return edge.target_node_id
				except Exception as e:print(f"LangGraph Router: Error evaluating condition for edge from '{current_node_id}' to '{edge.target_node_id}': {e}")
		for edge in outgoing_edges:
			if not edge.condition:print(f"LangGraph Router: From '{current_node_id}' to '{edge.target_node_id}' (default path)");return edge.target_node_id
		print(f"LangGraph Router: No valid edges from '{current_node_id}', routing to END.");return END
	def build_graph_from_definition(self,workflow_def):
		'\n        Build a LangGraph StateGraph from a workflow definition.\n        Handles nodes, conditional edges, and entry points.\n        ';graph_builder=StateGraph(DynamicWorkflowState)
		for node_def in workflow_def.graph.nodes:node_function=self._create_node_function(node_def);graph_builder.add_node(node_def.id,node_function);print(f"LangGraphService: Added node '{node_def.id}' to graph builder.")
		if not workflow_def.graph.entry_point:
			if workflow_def.graph.nodes:entry_point=workflow_def.graph.nodes[0].id;graph_builder.set_entry_point(entry_point);print(f"LangGraphService: No entry point specified, using first node '{entry_point}' as entry point.")
			else:raise ValueError('Workflow definition must have at least one node.')
		else:graph_builder.set_entry_point(workflow_def.graph.entry_point);print(f"LangGraphService: Set entry point to '{workflow_def.graph.entry_point}'.")
		if workflow_def.graph.edges:
			for edge_def in workflow_def.graph.edges:
				if edge_def.condition:conditional_fn=self._create_conditional_edge(edge_def);graph_builder.add_conditional_edges(edge_def.source_node_id,lambda state,edge=edge_def:self._create_conditional_edge(edge)(state));print(f"LangGraphService: Added conditional edge from '{edge_def.source_node_id}' to '{edge_def.target_node_id}' with condition '{edge_def.condition}'.")
				else:graph_builder.add_edge(edge_def.source_node_id,edge_def.target_node_id);print(f"LangGraphService: Added edge from '{edge_def.source_node_id}' to '{edge_def.target_node_id}'.")
		else:
			nodes=workflow_def.graph.nodes
			for i in range(len(nodes)-1):graph_builder.add_edge(nodes[i].id,nodes[i+1].id);print(f"LangGraphService: Added default linear edge from '{nodes[i].id}' to '{nodes[i+1].id}'.")
			if nodes:last_node=nodes[-1].id;graph_builder.add_edge(last_node,END);print(f"LangGraphService: Added default edge from '{last_node}' to END.")
		for node_def in workflow_def.graph.nodes:
			has_outgoing=any(edge.source_node_id==node_def.id for edge in workflow_def.graph.edges)
			if not has_outgoing:graph_builder.add_edge(node_def.id,END);print(f"LangGraphService: Added missing edge from '{node_def.id}' to END.")
		try:compiled_graph=graph_builder.compile(checkpointer=self.checkpoint_db);print('LangGraphService: Graph compiled successfully.');return compiled_graph
		except Exception as e:print(f"Error compiling LangGraph: {e}");raise
	async def execute_workflow(self,compiled_graph,initial_input):
		'\n        Execute a compiled workflow with the given input and return the results.\n        Tracks execution status and handles errors properly.\n        ';B='state';A='final_result'
		if not compiled_graph:raise ValueError('Compiled graph is not available for execution.')
		execution_id=f"exec-{uuid.uuid4().hex}";workflow_id=initial_input.get('workflow_id',f"workflow-{uuid.uuid4().hex}");initial_state=DynamicWorkflowState(original_task_description=initial_input.get(_S,''),current_sub_task_id='',sub_task_outputs={},final_result=_K,error_message='',execution_log=[],execution_start_time=datetime.now().isoformat(),execution_status=_L)
		for(key,value)in initial_input.items():
			if key not in initial_state:initial_state[key]=value
		config={'configurable':{'thread_id':f"thread-{execution_id}"}};print(f"LangGraphService: Executing workflow with input: {initial_input} and config: {config}");start_time=datetime.now()
		try:
			final_state=_K;execution_events=[]
			try:
				final_state_stream=compiled_graph.astream(initial_state,config=config)
				async for event_chunk in final_state_stream:
					if B in event_chunk:current_state=event_chunk[B];execution_events.append({_B:datetime.now().isoformat(),'event_type':'state_update',B:{'current_node':current_state.get(_I,''),'outputs':list(current_state.get(_A,{}).keys())}});final_state=current_state
			except Exception as e_stream:
				print(f"LangGraphService: Error during workflow streaming execution: {e_stream}")
				try:final_state=await compiled_graph.ainvoke(initial_state,config=config)
				except Exception as e_invoke:print(f"LangGraphService: Error during workflow invoke execution: {e_invoke}");raise e_invoke
			end_time=datetime.now();execution_time=(end_time-start_time).total_seconds()
			if final_state:
				final_state['execution_status']=_J if not final_state.get(_G)else _H
				if final_state.get(_G):return WorkflowExecutionResponse(workflow_id=workflow_id,execution_id=execution_id,status=_H,error=final_state.get(_G),logs=final_state.get(_F,[])+execution_events,execution_time=execution_time)
				if A not in final_state or not final_state[A]:final_state[A]=final_state.get(_A,{})
				print(f"LangGraphService: Workflow execution completed. Final state: {final_state}");return WorkflowExecutionResponse(workflow_id=workflow_id,execution_id=execution_id,status=_J,result=final_state.get(A),logs=final_state.get(_F,[])+execution_events,execution_time=execution_time)
			else:error_msg='Workflow execution did not yield a final state';return WorkflowExecutionResponse(workflow_id=workflow_id,execution_id=execution_id,status=_H,error=error_msg,logs=execution_events,execution_time=execution_time)
		except Exception as e:end_time=datetime.now();execution_time=(end_time-start_time).total_seconds();print(f"LangGraphService: Error during workflow execution: {e}");return WorkflowExecutionResponse(workflow_id=workflow_id,execution_id=execution_id,status=_H,error=str(e),logs=execution_events,execution_time=execution_time)