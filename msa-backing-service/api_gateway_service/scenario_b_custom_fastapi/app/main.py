from fastapi import FastAPI,Request,HTTPException,Depends
from fastapi.responses import StreamingResponse,JSONResponse
import httpx,asyncio
from typing import Optional,Dict,Any
from app.config import gateway_config,RouteConfig
from app.auth import verify_jwt_token,JWT_SECRET_KEY,JWT_ALGORITHM
from app.middleware import RateLimitingMiddleware,CustomHeaderMiddleware
SSL_KEYFILE='certs/selfsigned.key'
SSL_CERTFILE='certs/selfsigned.crt'
app=FastAPI(title='Custom API Gateway')
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(CustomHeaderMiddleware)
timeout_config=httpx.Timeout(1e1,read=2e1)
http_client=httpx.AsyncClient(timeout=timeout_config,follow_redirects=True)
@app.on_event('startup')
async def startup_event():
	print('Custom API Gateway started. Loaded routes:')
	if not gateway_config.routes:print('  No routes configured.')
	for A in gateway_config.routes:print(f"  - Path: {A.path_prefix}, Target: {A.target_base_url}, Auth: {A.requires_auth}")
@app.on_event('shutdown')
async def shutdown_event():await http_client.aclose();print('Custom API Gateway shut down.')
async def rate_limit_check(request,route_cfg):
	'특정 라우트에 대한 속도 제한 검사 (인메모리)';A=route_cfg
	if not A.rate_limit:return
	B=request.client.host;G=A.rate_limit.requests;H=A.rate_limit.per_seconds;C=A.path_prefix;from app.middleware import REQUEST_COUNTS as D;I=D[B][C];E=time.time();F=[A for A in I if A>E-H];D[B][C]=F
	if len(F)>=G:raise HTTPException(status_code=429,detail='Too Many Requests for this specific resource.')
	D[B][C].append(E)
@app.api_route('/{path:path}',methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'])
async def proxy_all_requests(request,path,token_payload=Depends(verify_jwt_token)):
	R='connection';S='transfer-encoding';M='error';N='host';O=path;H='content-type';E=token_payload;B='/';C=request;A=None;T=C.headers.get(N)
	for I in gateway_config.routes:
		if I.host and I.host!=T:continue
		if(B+O).startswith(I.path_prefix):
			if C.method in I.methods:A=I;break
	if not A:raise HTTPException(status_code=404,detail='Endpoint not found or method not allowed.')
	if A.requires_auth:
		if not E:raise HTTPException(status_code=401,detail='Authentication required: No token provided.')
		if E.get(M):raise HTTPException(status_code=401,detail=f"Authentication failed: {E.get(M)}")
	try:await rate_limit_check(C,A)
	except HTTPException as D:raise D
	F=O
	if A.strip_prefix:F=O[len(A.path_prefix.lstrip(B)):]
	if A.target_base_url.path.endswith(B)and F.startswith(B):J=f"{A.target_base_url.rstrip(B)}{F}"
	elif not A.target_base_url.path.endswith(B)and not F.startswith(B):J=f"{A.target_base_url}/{F}"
	else:J=f"{A.target_base_url.rstrip(B)}/{F.lstrip(B)}"
	if C.query_params:J+=f"?{C.query_params}"
	K={A:B for(A,B)in C.headers.items()if A.lower()not in[N,S,R]};K['X-Original-Host']=C.headers.get(N,'')
	if A.add_headers:
		for(P,Q)in A.add_headers.items():K[P]=Q
	if A.requires_auth and E and not E.get(M):U=E.get('sub','unknown');K['X-Authenticated-User-Id']=U
	V=await C.body()
	try:
		G=await http_client.request(method=C.method,url=J,headers=K,content=V);L={A:B for(A,B)in G.headers.items()if A.lower()not in['content-encoding','content-length',S,R]}
		if A.transform_response_headers:
			for(P,Q)in A.transform_response_headers.items():L[P]=Q
		if H not in L and G.headers.get(H):L[H]=G.headers.get(H)
		return StreamingResponse(G.aiter_bytes(),status_code=G.status_code,headers=L,media_type=G.headers.get(H))
	except httpx.TimeoutException as D:raise HTTPException(status_code=504,detail=f"Gateway timeout: {D}")
	except httpx.ConnectError as D:raise HTTPException(status_code=502,detail=f"Bad gateway: Unable to connect to upstream service: {D}")
	except httpx.RequestError as D:raise HTTPException(status_code=500,detail=f"Gateway error: {D}")
	except Exception as D:raise HTTPException(status_code=500,detail=f"Internal server error in gateway: {D}")
@app.get('/get-test-jwt/{user_id}')
async def get_test_jwt_endpoint(user_id):A=user_id;import datetime as B;C={'sub':A,'iss':'custom-gw-auth-test-issuer','exp':B.datetime.utcnow()+B.timedelta(hours=1)};D=jwt.encode(C,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM);return{'user_id':A,'token_type':'Bearer','access_token':D}
if __name__=='__main__':import uvicorn;uvicorn.run(app,host='0.0.0.0',port=8000)