_D='application/json'
_C='LLMService model not initialized.'
_B='```'
_A='```json'
from vertexai.generative_models import GenerativeModel,Part,GenerationConfig
from app.core.config import settings
from app.schemas.task import TaskDecompositionRequest,TaskDecompositionResponse,SubTask
import json
class LLMService:
	def __init__(self,model_id=settings.DEFAULT_LLM_MODEL_ID):
		try:from google.cloud import aiplatform;aiplatform.init(project=settings.VERTEX_AI_PROJECT_ID,location=settings.VERTEX_AI_LOCATION);self.model=GenerativeModel(model_id);print(f"LLMService initialized with model: {model_id}")
		except ImportError as e:print(f"Missing Google Cloud dependencies: {e}");raise
		except Exception as e:
			print(f"Failed to initialize GenerativeModel: {e}")
			if'permissions'in str(e).lower()or'credentials'in str(e).lower():print('This may be a credentials issue. Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly.')
			self.model=None
	async def decompose_task(self,task_description):
		if not self.model:raise ConnectionError(_C)
		prompt=f'''
        You are an expert task decomposition system. Break down the following complex task into a sequence of smaller, manageable sub-tasks.

        TASK: "{task_description}"

        OUTPUT INSTRUCTIONS:
        1. Return valid JSON with a "sub_tasks" array
        2. Each sub-task should have:
          - "id": String ID (format: "subtask_1", "subtask_2", etc.)
          - "description": Clear, actionable description
          - "depends_on": Array of IDs this sub-task depends on
          - "assigned_agent_type": Suggested agent capability type
          - "required_tools": Array of specific tools needed

        EXAMPLE OUTPUT:
        {{
          "sub_tasks": [
            {{
              "id": "subtask_1",
              "description": "Search for recent climate data from 2023-2025",
              "depends_on": [],
              "assigned_agent_type": "research_agent",
              "required_tools": ["web_search"]
            }},
            {{
              "id": "subtask_2",
              "description": "Analyze temperature trends from the collected data",
              "depends_on": ["subtask_1"],
              "assigned_agent_type": "data_analyzer",
              "required_tools": ["data_analysis", "visualization"]
            }}
          ]
        }}

        RETURN ONLY VALID JSON:
        '''
		try:
			response=await self.model.generate_content_async(prompt,generation_config=GenerationConfig(temperature=.2,response_mime_type=_D,max_output_tokens=2048));json_output_str=''
			if response.candidates and response.candidates[0].content.parts:
				json_output_str=response.candidates[0].content.parts[0].text;json_output_str=json_output_str.strip()
				if json_output_str.startswith(_A):json_output_str=json_output_str.replace(_A,'',1).strip()
				if json_output_str.endswith(_B):json_output_str=json_output_str.rsplit(_B,1)[0].strip()
				try:parsed_json=json.loads(json_output_str)
				except json.JSONDecodeError:
					import re;json_match=re.search('\\{[\\s\\S]*\\}',json_output_str)
					if json_match:
						try:parsed_json=json.loads(json_match.group(0))
						except:raise ValueError(f"Failed to parse JSON after extraction attempt")
					else:raise ValueError('Could not locate valid JSON in model response')
				sub_task_data_list=parsed_json.get('sub_tasks',[]);sub_tasks=[SubTask(**st_data)for st_data in sub_task_data_list];return TaskDecompositionResponse(original_task=task_description,sub_tasks=sub_tasks)
			else:raise ValueError('Empty or invalid response from LLM')
		except Exception as e:print(f"Error during task decomposition: {e}");print(f"Raw response text: {json_output_str if"json_output_str"in locals()else"N/A"}");raise
	from typing import Dict,Any,List,Optional
	async def generate_node_config_from_subtask(self,sub_task,overall_task_context):
		'\n        Generate specific configuration for a LangGraph node based on a sub-task.\n        ';L='generic_task_node';K='error';J='str';I='result';H='output_schema';G='Any';F='input_schema';E='processing_node';D='instruction';C='type';B='tool_node';A='llm_node'
		if not self.model:raise ConnectionError(_C)
		node_type=A
		if sub_task.required_tools and any(tool in['web_search','database_query','api_call']for tool in sub_task.required_tools):node_type=B
		elif sub_task.assigned_agent_type and'analyzer'in sub_task.assigned_agent_type:node_type=E
		prompt=f'''
        TASK CONTEXT: "{overall_task_context}"
        SUBTASK: "{sub_task.description}"
        AGENT TYPE: "{sub_task.assigned_agent_type or"general_purpose_agent"}"
        REQUIRED TOOLS: {sub_task.required_tools if sub_task.required_tools else[]}
        
        Create a detailed configuration for a LangGraph node of type "{node_type}" to handle this subtask.
        
        {"For an LLM node, provide the exact prompt template to use."if node_type==A else""}
        {"For a tool node, specify the tool to use and how to construct the input query."if node_type==B else""}
        {"For a processing node, specify the data processing operations to perform."if node_type==E else""}
        
        Return a JSON object with:
        - "type": The node type ("{node_type}")
        - "name": A short descriptive name for this node
        - "config": The complete configuration needed
        
        EXAMPLE OUTPUT FOR {node_type.upper()}:
        {{"type": "{node_type}", "name": "example_node", "config": {{
            {"prompt_template": "Analyze the following data: { {input_data}}"" if node_type == "llm_node" else ""}
            {"tool_name": "web_search", "input_mapping": { {"query":"{{topic}} latest information 2025"}}" if node_type == "tool_node" else ""}
            {"operations": ["filter", "aggregate"], "parameters": { {"filter_key":"value > 10"}}" if node_type == "processing_node" else ""}
        }}}}
        
        RETURN ONLY VALID JSON:
        '''
		try:
			response=await self.model.generate_content_async(prompt,generation_config=GenerationConfig(temperature=.3,response_mime_type=_D))
			if response.candidates and response.candidates[0].content.parts:
				json_output_str=response.candidates[0].content.parts[0].text;json_output_str=json_output_str.strip()
				if json_output_str.startswith(_A):json_output_str=json_output_str.replace(_A,'',1).strip()
				if json_output_str.endswith(_B):json_output_str=json_output_str.rsplit(_B,1)[0].strip()
				try:
					parsed_json=json.loads(json_output_str);parsed_json['metadata']={'created_at':datetime.now().isoformat(),'sub_task_id':sub_task.id,'depends_on':sub_task.depends_on}
					if node_type==A:parsed_json[F]={'input_data':G};parsed_json[H]={I:J}
					elif node_type==B:parsed_json[F]={'topic':J};parsed_json[H]={I:G}
					return parsed_json
				except json.JSONDecodeError as e:print(f"Error parsing JSON: {e}");return{C:node_type,'name':f"node_{sub_task.id}",'config':{D:sub_task.description}}
			else:return{C:L,D:sub_task.description,K:'Empty LLM response'}
		except Exception as e:print(f"Error generating node config: {e}");return{C:L,D:sub_task.description,K:str(e)}