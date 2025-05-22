from fastapi import Request,HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import jwt
from typing import Optional
JWT_SECRET_KEY='your-super-secret-key'
JWT_ALGORITHM='HS256'
oauth2_scheme=HTTPBearer(auto_error=False)
async def verify_jwt_token(token=Depends(oauth2_scheme)):
	'\n    JWT 토큰을 검증하고 payload를 반환합니다.\n    토큰이 없거나 유효하지 않으면 None을 반환 (라우트 핸들러에서 requires_auth 플래그에 따라 처리).\n    ';A='error';B=token
	if B is None:return
	E=HTTPException(status_code=401,detail='Could not validate credentials',headers={'WWW-Authenticate':'Bearer'})
	try:C=jwt.decode(B.credentials,JWT_SECRET_KEY,algorithms=[JWT_ALGORITHM]);return C
	except jwt.ExpiredSignatureError:return{A:'Token has expired'}
	except jwt.PyJWTError as D:return{A:f"Invalid token: {str(D)}"}
def generate_test_jwt(user_id):'테스트용 JWT 토큰 생성 함수';import datetime as A;B={'sub':user_id,'iss':'custom-gw-auth','exp':A.datetime.utcnow()+A.timedelta(hours=1)};C=jwt.encode(B,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM);return C
if __name__=='__main__':test_token=generate_test_jwt('testuser123');print(f"Generated Test JWT: Bearer {test_token}")