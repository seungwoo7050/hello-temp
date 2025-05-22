_F='content'
_E='title'
_D='Elasticsearch client not available.'
_C=True
_B='filter'
_A=None
from fastapi import FastAPI,HTTPException,Query
from elasticsearch import Elasticsearch,exceptions
from pydantic import BaseModel
from typing import List,Dict,Any,Optional
app=FastAPI(title='Search Service Interaction API',description='An example API to interact with Elasticsearch for indexing and searching documents.',version='0.1.0')
ES_HOST_MSA='search_engine_service'
ES_PORT_MSA=9200
ES_HOST_LOCAL='localhost'
ES_PORT_LOCAL=19200
try:
	es_client=Elasticsearch(f"http://{ES_HOST_MSA}:{ES_PORT_MSA}")
	if not es_client.ping():raise exceptions.ConnectionError('Failed to ping Elasticsearch (MSA config)')
	print(f"Successfully connected to Elasticsearch (MSA config): http://{ES_HOST_MSA}:{ES_PORT_MSA}")
except exceptions.ConnectionError:
	print(f"Could not connect to Elasticsearch with MSA config (http://{ES_HOST_MSA}:{ES_PORT_MSA}). Trying local config...")
	try:
		es_client=Elasticsearch(f"http://{ES_HOST_LOCAL}:{ES_PORT_LOCAL}")
		if not es_client.ping():raise exceptions.ConnectionError('Failed to ping Elasticsearch (Local config)')
		print(f"Successfully connected to Elasticsearch (Local config): http://{ES_HOST_LOCAL}:{ES_PORT_LOCAL}")
	except exceptions.ConnectionError as e:print(f"Failed to connect to Elasticsearch with both MSA and Local configs: {e}");es_client=_A
class Document(BaseModel):id:Optional[str]=_A;title:str;content:str;tags:Optional[List[str]]=_A;author:Optional[str]=_A
class IndexStatus(BaseModel):acknowledged:bool;index:str
class SearchResult(BaseModel):id:str;score:float;source:Dict[str,Any];highlight:Optional[Dict[str,List[str]]]=_A
async def ensure_index_exists(index_name):
	K='keyword';J='text';I='search_analyzer';H='nori_posfilter';G='tokenizer';E='nori_tokenizer';D='analyzer';C='nori_korean_analyzer';B=index_name;A='type'
	if not es_client:raise HTTPException(status_code=503,detail=_D)
	try:
		if not await es_client.indices.exists(index=B):L={'settings':{'analysis':{D:{C:{A:'custom',G:E,_B:[H,'lowercase']}},G:{E:{A:E,'decompound_mode':'mixed','user_dictionary':'user_dict_ko.txt'}},_B:{H:{A:'nori_part_of_speech','stoptags':['E','IC','J','XSV','XSA','SP']}}}},'mappings':{'properties':{_E:{A:J,D:C,I:C},_F:{A:J,D:C,I:C},'tags':{A:K},'author':{A:K},'created_at':{A:'date'}}}};await es_client.indices.create(index=B,body=L);print(f"Index '{B}' created with Nori analyzer settings.")
	except exceptions.ElasticsearchException as F:print(f"Error checking/creating index '{B}': {F}");raise HTTPException(status_code=500,detail=f"Could not ensure index '{B}' exists: {str(F)}")
@app.on_event('startup')
async def startup_event():
	if not es_client:print('CRITICAL: Elasticsearch client is not initialized. API may not function.');return
	await ensure_index_exists(index_name='my_documents')
@app.post('/index/{index_name}',response_model=IndexStatus,status_code=201)
async def index_document(index_name,doc):
	'\n    새로운 문서를 지정된 인덱스에 추가합니다.\n    문서 ID를 제공하지 않으면 Elasticsearch가 자동으로 생성합니다.\n    ';B=index_name;A=doc
	if not es_client:raise HTTPException(status_code=503,detail=_D)
	try:
		if A.id:C=await es_client.index(index=B,id=A.id,document=A.model_dump(exclude_none=_C))
		else:C=await es_client.index(index=B,document=A.model_dump(exclude_none=_C))
		return IndexStatus(acknowledged=_C if C.get('result')in['created','updated']else False,index=C.get('_index'))
	except exceptions.ElasticsearchException as D:print(f"Error indexing document in '{B}': {D}");raise HTTPException(status_code=500,detail=f"Error indexing document: {str(D)}")
@app.get('/search/{index_name}',response_model=List[SearchResult])
async def search_documents(index_name,query=Query(...,description="검색어 (예: '한국어 검색 테스트')"),size=Query(10,ge=1,le=100,description='반환할 결과 수'),author=Query(_A,description='작성자 필터링'),highlight_enabled=Query(_C,description='검색어 하이라이팅 사용 여부')):
	"\n    지정된 인덱스에서 문서를 검색합니다.\n    - 'query' 파라미터로 전문 검색(full-text search)을 수행합니다.\n    - 'author' 파라미터로 필터링할 수 있습니다.\n    - 'highlight_enabled'로 검색어 하이라이팅을 켤 수 있습니다.\n    ";L='hits';K='highlight';J='fields';I='bool';G=author;F=query;E='query';B=index_name
	if not es_client:raise HTTPException(status_code=503,detail=_D)
	C={E:{I:{'must':[{'multi_match':{E:F,J:[_E,_F],'operator':'and'}}],_B:[]}},'size':size}
	if G:C[E][I][_B].append({'term':{'author.keyword':G}})
	if highlight_enabled:C[K]={J:{_E:{},_F:{}},'pre_tags':['<mark>'],'post_tags':['</mark>']}
	try:
		M=await es_client.search(index=B,body=C);H=[]
		for A in M[L][L]:H.append(SearchResult(id=A['_id'],score=A['_score'],source=A['_source'],highlight=A.get(K)))
		return H
	except exceptions.ElasticsearchException as D:
		print(f"Error searching in '{B}' with query '{F}': {D}")
		if isinstance(D,exceptions.NotFoundError):raise HTTPException(status_code=404,detail=f"Index '{B}' not found.")
		raise HTTPException(status_code=500,detail=f"Error during search: {str(D)}")
@app.get('/health')
async def health_check():
	if not es_client or not await es_client.ping():raise HTTPException(status_code=503,detail='Elasticsearch service is unavailable.')
	return{'status':'ok','elasticsearch_connection':'active'}