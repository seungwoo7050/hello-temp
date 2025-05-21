_J=False
_I='FAILURE'
_H='SUCCESS'
_G='completion_reason'
_F='completion_status'
_E='is_complete'
_D='\n'
_C='text'
_B='message_content'
_A=None
from app.schemas.a2a import A2AMessageContent
from typing import Dict,Any,Optional,List
from app.core.config import settings
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
class A2AProtocolFormat:"Constants for A2A protocol message formats based on Google's A2A protocol spec";MESSAGE_HEADER='## A2A-MESSAGE';SOURCE_PREFIX='FROM:';TARGET_PREFIX='TO:';INTERACTION_PREFIX='INTERACTION:';GOAL_PREFIX='GOAL:';MESSAGE_TYPE_PREFIX='TYPE:';CONTENT_SEPARATOR='## CONTENT:';COMPLETION_MARKER='## COMPLETION:';COMPLETION_STATUS_SUCCESS=_H;COMPLETION_STATUS_FAILURE=_I;COMPLETION_REASON_PREFIX='REASON:'
class A2AProtocolHandler:
	def __init__(A):
		A.llm=_A
		if settings.ENABLE_LLM_PROCESSING and settings.VERTEX_PROJECT_ID and settings.VERTEX_LOCATION:
			try:aiplatform.init(project=settings.VERTEX_PROJECT_ID,location=settings.VERTEX_LOCATION);A.llm=GenerativeModel('gemini-1.5-pro');print('A2AProtocolHandler initialized with LLM support.')
			except Exception as B:print(f"Error initializing LLM: {B}");print('A2AProtocolHandler will operate without LLM support.')
		else:print('A2AProtocolHandler initialized without LLM support.')
	def generate_initial_prompt_for_source_agent(I,source_agent_name,target_agent_name,goal,interaction_id,initial_content=_A):
		"\n        Generate the initial prompt for the source agent in an A2A interaction.\n        Follows Google's A2A protocol format.\n        \n        Args:\n            source_agent_name: Name of the source agent\n            target_agent_name: Name of the target agent\n            goal: Goal of the interaction\n            interaction_id: Unique ID for the interaction\n            initial_content: Optional initial content for the interaction\n            \n        Returns:\n            Formatted prompt string for the source agent\n        ";E=source_agent_name;D=goal;C=initial_content;B=target_agent_name;G=f"""You are '{E}' and you are working with '{B}' to achieve the following goal: '{D}'. You will communicate with '{B}' using a structured protocol format. Follow these guidelines:

1. Be clear about what information or action you need from '{B}'.
2. Provide context necessary for '{B}' to assist you.
3. When the goal is achieved, include '{A2AProtocolFormat.COMPLETION_MARKER} {A2AProtocolFormat.COMPLETION_STATUS_SUCCESS}' in your message.
4. If the goal cannot be achieved, include '{A2AProtocolFormat.COMPLETION_MARKER} {A2AProtocolFormat.COMPLETION_STATUS_FAILURE}' followed by '{A2AProtocolFormat.COMPLETION_REASON_PREFIX} [reason]'.

""";A=f"""{A2AProtocolFormat.MESSAGE_HEADER}
{A2AProtocolFormat.SOURCE_PREFIX} {E}
{A2AProtocolFormat.TARGET_PREFIX} {B}
{A2AProtocolFormat.INTERACTION_PREFIX} {interaction_id}
{A2AProtocolFormat.GOAL_PREFIX} {D}
"""
		if C:
			F=C.type;A+=f"{A2AProtocolFormat.MESSAGE_TYPE_PREFIX} {F}\n";A+=f"{A2AProtocolFormat.CONTENT_SEPARATOR}\n"
			if F==_C:A+=C.payload
			else:A+=str(C.payload)
		else:A+=f"{A2AProtocolFormat.MESSAGE_TYPE_PREFIX} text\n";A+=f"{A2AProtocolFormat.CONTENT_SEPARATOR}\n";A+=f"Hello {B}, I need your assistance to achieve our goal: {D}. Let's start working together."
		H=G+_D+A+'\n\n'+f"Now, craft your first message to {B}:";return H
	async def parse_agent_response(E,response_text,source_agent_id,target_agent_id,interaction_id):
		"\n        Parse an agent's response text to extract A2A protocol elements.\n        Can use LLM assistance if available.\n        \n        Args:\n            response_text: Raw text response from the agent\n            source_agent_id: ID of the source agent\n            target_agent_id: ID of the target agent\n            interaction_id: ID of the interaction\n            \n        Returns:\n            Dict containing message content and completion status\n        ";A=response_text;B={_B:_A,_E:_J,_F:_A,_G:_A}
		if E.llm:
			try:return await E._parse_with_llm(A,source_agent_id,target_agent_id,interaction_id)
			except Exception as K:print(f"Error using LLM to parse response: {K}");print('Falling back to rule-based parsing')
		C=A.find(A2AProtocolFormat.CONTENT_SEPARATOR)
		if C!=-1:
			C+=len(A2AProtocolFormat.CONTENT_SEPARATOR);F=A.find(A2AProtocolFormat.COMPLETION_MARKER,C)
			if F!=-1:G=A[C:F].strip()
			else:G=A[C:].strip()
			B[_B]=A2AMessageContent(type=_C,payload=G)
		else:B[_B]=A2AMessageContent(type=_C,payload=A)
		if A2AProtocolFormat.COMPLETION_MARKER in A:
			B[_E]=True;H=A.find(A2AProtocolFormat.COMPLETION_MARKER);I=A[H:].split(_D)[0]
			if A2AProtocolFormat.COMPLETION_STATUS_SUCCESS in I:B[_F]=_H
			elif A2AProtocolFormat.COMPLETION_STATUS_FAILURE in I:
				B[_F]=_I;D=A.find(A2AProtocolFormat.COMPLETION_REASON_PREFIX,H)
				if D!=-1:
					D+=len(A2AProtocolFormat.COMPLETION_REASON_PREFIX);J=A.find(_D,D)
					if J!=-1:B[_G]=A[D:J].strip()
					else:B[_G]=A[D:].strip()
		return B
	async def _parse_with_llm(D,response_text,source_agent_id,target_agent_id,interaction_id):
		'\n        Use LLM to parse agent response with more intelligence.\n        \n        Args:\n            response_text: Raw text response from the agent\n            source_agent_id: ID of the source agent\n            target_agent_id: ID of the target agent\n            interaction_id: ID of the interaction\n            \n        Returns:\n            Dict containing parsed message content and completion status\n        ';B=response_text;E=f'''
        Parse the following A2A protocol agent response and extract structured information:
        
        {B}
        
        Extract and return a JSON object with the following fields:
        1. message_content: The main content of the message
        2. is_complete: Boolean indicating if the interaction is marked as complete
        3. completion_status: "SUCCESS" or "FAILURE" if is_complete is true, otherwise null
        4. completion_reason: Reason for completion if status is "FAILURE", otherwise null
        
        The A2A protocol uses these markers:
        - Content separator: "{A2AProtocolFormat.CONTENT_SEPARATOR}"
        - Completion marker: "{A2AProtocolFormat.COMPLETION_MARKER}"
        - Success status: "{A2AProtocolFormat.COMPLETION_STATUS_SUCCESS}"
        - Failure status: "{A2AProtocolFormat.COMPLETION_STATUS_FAILURE}"
        - Reason prefix: "{A2AProtocolFormat.COMPLETION_REASON_PREFIX}"
        
        Return ONLY the JSON object, nothing else.
        ''';F=D.llm.generate_content(E);G=F.text
		try:
			import json,re;H='\\{.*\\}';C=re.search(H,G,re.DOTALL)
			if C:
				I=C.group(0);A=json.loads(I)
				if _B in A and A[_B]:A[_B]=A2AMessageContent(type=_C,payload=A[_B])
				else:A[_B]=A2AMessageContent(type=_C,payload='[No content extracted]')
				return A
			else:print('No valid JSON found in LLM response')
		except Exception as J:print(f"Error parsing JSON from LLM response: {J}")
		return{_B:A2AMessageContent(type=_C,payload=B),_E:_J,_F:_A,_G:_A}
	def wrap_content_for_target_agent(G,content_from_source,source_agent_name,target_agent_name,interaction_id,goal):
		"\n        Format a message from the source agent for delivery to the target agent.\n        Follows Google's A2A protocol format.\n        \n        Args:\n            content_from_source: Content from the source agent\n            source_agent_name: Name of the source agent\n            target_agent_name: Name of the target agent\n            interaction_id: ID of the interaction\n            goal: Goal of the interaction\n            \n        Returns:\n            Formatted message string for the target agent\n        ";D=target_agent_name;A=source_agent_name;B=content_from_source;E=f"""You are '{D}' and you are collaborating with '{A}' to achieve the following goal: '{goal}'. You have received a message from '{A}' using the A2A protocol format. Follow these guidelines:

1. Focus on addressing the specific request or providing the information requested.
2. Include any relevant context or clarification questions if needed.
3. When the goal is fully achieved, include '{A2AProtocolFormat.COMPLETION_MARKER} {A2AProtocolFormat.COMPLETION_STATUS_SUCCESS}' in your message.
4. If you cannot fulfill the request, include '{A2AProtocolFormat.COMPLETION_MARKER} {A2AProtocolFormat.COMPLETION_STATUS_FAILURE}' followed by '{A2AProtocolFormat.COMPLETION_REASON_PREFIX} [reason]'.

""";C=f"""{A2AProtocolFormat.MESSAGE_HEADER}
{A2AProtocolFormat.SOURCE_PREFIX} {A}
{A2AProtocolFormat.TARGET_PREFIX} {D}
{A2AProtocolFormat.INTERACTION_PREFIX} {interaction_id}
{A2AProtocolFormat.GOAL_PREFIX} {goal}
{A2AProtocolFormat.MESSAGE_TYPE_PREFIX} {B.type}
{A2AProtocolFormat.CONTENT_SEPARATOR}
"""
		if B.type==_C:C+=B.payload
		else:C+=str(B.payload)
		F=E+_D+C+'\n\n'+f"Now, craft your response to {A}:";return F
	def detect_completion(I,message_text):
		'\n        Detect if an interaction is complete based on a message.\n        \n        Args:\n            message_text: Text message to analyze\n            \n        Returns:\n            Dict containing completion status and reason if found\n        ';D='reason';E='status';A=message_text;B={_E:_J,E:_A,D:_A}
		if A2AProtocolFormat.COMPLETION_MARKER in A:
			B[_E]=True;F=A.find(A2AProtocolFormat.COMPLETION_MARKER);G=A[F:].split(_D)[0]
			if A2AProtocolFormat.COMPLETION_STATUS_SUCCESS in G:B[E]=_H
			elif A2AProtocolFormat.COMPLETION_STATUS_FAILURE in G:
				B[E]=_I;C=A.find(A2AProtocolFormat.COMPLETION_REASON_PREFIX,F)
				if C!=-1:
					C+=len(A2AProtocolFormat.COMPLETION_REASON_PREFIX);H=A.find(_D,C)
					if H!=-1:B[D]=A[C:H].strip()
					else:B[D]=A[C:].strip()
		return B
	async def restructure_message_with_llm(B,message_content,source_agent_name,target_agent_name,interaction_id,goal):
		'\n        Use LLM to restructure a message for better clarity and protocol alignment.\n        \n        Args:\n            message_content: Message content to restructure\n            source_agent_name: Name of the source agent\n            target_agent_name: Name of the target agent\n            interaction_id: ID of the interaction\n            goal: Goal of the interaction\n            \n        Returns:\n            Restructured message content\n        ';A=message_content
		if not B.llm:return A
		try:C=f"""
            You are helping with communication between two AI agents.
            
            SOURCE AGENT: {source_agent_name}
            TARGET AGENT: {target_agent_name}
            GOAL: {goal}
            
            The following message needs to be restructured to better follow the A2A protocol format:
            
            {A.payload}
            
            Please restructure this message to:
            1. Be clear and concise
            2. Focus on achieving the goal
            3. Follow proper communication protocol between agents
            4. Maintain all important information from the original message
            
            Return ONLY the restructured message content.
            """;D=B.llm.generate_content(C);return A2AMessageContent(type=A.type,payload=D.text)
		except Exception as E:print(f"Error using LLM to restructure message: {E}");return A