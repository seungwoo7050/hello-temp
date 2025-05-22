from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware,RequestResponseEndpoint
from starlette.responses import Response
import time
from collections import defaultdict
from app.config import gateway_config,RouteConfig
REQUEST_COUNTS=defaultdict(lambda:defaultdict(list))
class RateLimitingMiddleware(BaseHTTPMiddleware):
	async def dispatch(C,request,call_next):A=request;D=A.client.host;B=await call_next(A);return B
class CustomHeaderMiddleware(BaseHTTPMiddleware):
	async def dispatch(B,request,call_next):A=await call_next(request);return A