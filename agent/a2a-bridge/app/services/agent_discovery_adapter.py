_B='a2a-communication'
_A='capabilities'
import httpx
from app.core.config import settings
from app.schemas.a2a import DiscoveredAgent
from typing import List,Optional,Dict,Any
import logging
logger=logging.getLogger(__name__)
class AgentDiscoveryAdapter:
	def __init__(A):
		A.agent_registry_url=settings.AGENT_REGISTRY_SERVICE_URL
		if not A.agent_registry_url:logger.warning('AGENT_REGISTRY_SERVICE_URL not configured. Agent discovery functions will be limited.')
		else:logger.info(f"AgentDiscoveryAdapter initialized with registry URL: {A.agent_registry_url}")
	async def find_agent_by_id(C,agent_id):
		'\n        Find an agent by its ID from the Agent Registry\n        \n        Args:\n            agent_id: External ID of the agent to find\n            \n        Returns:\n            DiscoveredAgent object if found, None otherwise\n        ';B=agent_id
		if not C.agent_registry_url:logger.error('Agent Registry URL not configured. Cannot discover agents.');return
		try:
			async with httpx.AsyncClient(timeout=1e1)as E:D=await E.get(f"{C.agent_registry_url}/registry/{B}");D.raise_for_status();F=D.json();return C._parse_agent_data(F)
		except httpx.HTTPStatusError as A:
			if A.response.status_code==404:logger.info(f"Agent '{B}' not found in registry");return
			logger.error(f"HTTP error discovering agent '{B}': {A.response.status_code}");return
		except httpx.RequestError as A:logger.error(f"Request error discovering agent '{B}': {A}");return
		except Exception as A:logger.error(f"Unexpected error discovering agent '{B}': {A}");return
	async def list_available_a2a_agents(B):
		'\n        Get a list of all agents capable of A2A communication from the Agent Registry\n        \n        Returns:\n            List of DiscoveredAgent objects with A2A capability\n        '
		if not B.agent_registry_url:logger.error('Agent Registry URL not configured. Cannot list agents.');return[]
		try:
			async with httpx.AsyncClient(timeout=15.)as F:
				D=await F.get(f"{B.agent_registry_url}/registry/match",params={_A:[_B]});D.raise_for_status();G=D.json();C=[]
				for H in G:
					E=B._parse_agent_data(H)
					if E:C.append(E)
				logger.info(f"Discovered {len(C)} A2A-capable agents");return C
		except httpx.HTTPStatusError as A:logger.error(f"HTTP error listing A2A agents: {A.response.status_code}");return[]
		except httpx.RequestError as A:logger.error(f"Request error listing A2A agents: {A}");return[]
		except Exception as A:logger.error(f"Unexpected error listing A2A agents: {A}");return[]
	def _parse_agent_data(F,agent_data):
		'\n        Parse agent data from the Agent Registry into a DiscoveredAgent object\n        \n        Args:\n            agent_data: JSON data from the Agent Registry\n            \n        Returns:\n            DiscoveredAgent object or None if parsing fails\n        ';B='name';A=agent_data
		try:
			C=[]
			if _A in A and isinstance(A[_A],list):C=[A.get(B)if isinstance(A,dict)else A for A in A[_A]if isinstance(A,dict)and B in A or isinstance(A,str)]
			if _B not in C and'a2a_communication'not in C:logger.debug(f"Agent {A.get(B)} doesn't have A2A capability")
			D=A.get('agent_id_external',A.get('agent_id',A.get('id')))
			if not D:logger.warning(f"Could not find agent_id in response: {A}");return
			return DiscoveredAgent(agent_id=D,name=A.get(B,'Unknown Agent'),description=A.get('description',''),capabilities=C,metadata=A.get('metadata',{}))
		except Exception as E:logger.error(f"Error parsing agent data: {E}");return
	async def find_agents_by_capability(A,capability):
		'\n        Find agents with a specific capability\n        \n        Args:\n            capability: Capability to search for\n            \n        Returns:\n            List of DiscoveredAgent objects with the specified capability\n        ';B=capability
		if not A.agent_registry_url:logger.error('Agent Registry URL not configured. Cannot find agents by capability.');return[]
		try:
			async with httpx.AsyncClient(timeout=1e1)as F:
				D=await F.get(f"{A.agent_registry_url}/registry/match",params={_A:[B]});D.raise_for_status();G=D.json();C=[]
				for H in G:
					E=A._parse_agent_data(H)
					if E:C.append(E)
				logger.info(f"Found {len(C)} agents with capability '{B}'");return C
		except Exception as I:logger.error(f"Error finding agents with capability '{B}': {I}");return[]