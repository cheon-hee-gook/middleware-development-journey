from fastapi import FastAPI, HTTPException, Request, Depends
from starlette.middleware import Middleware
from starlette.responses import Response, JSONResponse
import json

from app.auth import create_jwt
from app.database import users_db
# from app.middleware import (BasicRequestLoggingMiddleware, RequestBodyLoggingMiddleware, ResponseLoggingMiddleware, ProcessingTimeLoggingMiddleware)
# from app.middleware import JWTAuthenticationMiddlewareBaseHTTPMiddleware, JWTAuthenticationMiddlewareStarlette, RoleAuthorizationMiddlewareBaseHTTPMiddleware, RoleAuthorizationMiddlewareStarlette
from app.middleware import RequestEncryptionMiddleware, RequestDecryptionMiddleware, RequestValidationMiddleware
from app.schemas import LoginRequest, ExampleRequestModel

app = FastAPI(lifespan=None)

# 요청 로깅 미들웨어 등록
# app.add_middleware(BasicRequestLoggingMiddleware)

# 요청 본문 로깅 미들웨어 등록
# app.add_middleware(RequestBodyLoggingMiddleware)

# 응답 로깅 미들웨어 등록
# app.add_middleware(ResponseLoggingMiddleware)

# 처리 시간 로깅 미들웨어 등록
# app.add_middleware(ProcessingTimeLoggingMiddleware)

# 권한 관리 미들웨어 등록
# app.add_middleware(RoleAuthorizationMiddlewareStarlette, required_roles=["admin"])
# app.add_middleware(RoleAuthorizationMiddlewareBaseHTTPMiddleware, required_roles=["admin"])

# JWT 인증 미들웨어 등록
# app.add_middleware(JWTAuthenticationMiddlewareStarlette, excluded_paths=["/", "/token"])
# app.add_middleware(JWTAuthenticationMiddlewareBaseHTTPMiddleware, excluded_paths=["/", "/token"])

# 암호화 미들웨어 등록
# app.add_middleware(RequestEncryptionMiddleware)

# 복호화 미들웨어 등록
# app.add_middleware(RequestDecryptionMiddleware)

# 요청 검증 미들웨어 등록
app.add_middleware(RequestValidationMiddleware, model=ExampleRequestModel)


@app.get("/")
async def root():
    return {"message": "Hello, Middleware!"}


@app.post("/data")
async def receive_data(payload: dict):
    if "key" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'key' in payload")
    return {"received_key": payload["key"]}


@app.get("/data")
async def get_data():
    from faker import Faker
    import time
    fake = Faker("ko_KR")
    Faker.seed(42)

    email = { str(i+1): fake.unique.free_email() for i in range(10)}
    time.sleep(3)
    return email


@app.post("/token")
async def login(request: LoginRequest):
    username = request.username
    password = request.password

    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_jwt(username, user['role'])
    return {"access_token": token, "token_type": "Bearer"}


@app.get("/protected")
def protected_resource(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        return {"message": "Unauthorized access"}
    return {"message": f"Hello, {user['sub']}!"}


@app.get("/admin")
async def admin_resource(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        return {"message": "Unauthorized access"}
    return {"message": f"Hello, {user['sub']}!"}


@app.post("/secure-data")
async def secure_data(request: Request):
    """요청 데이터를 처리하여 응답"""
    try:
        # 요청 본문 데이터 읽기
        body = await request.body()

        # 복호화된 데이터를 JSON으로 변환
        if body:
            body_json = json.loads(body)
        else:
            raise ValueError("Empty body")

        # 처리된 데이터를 반환
        return {"received": body_json}

    except json.JSONDecodeError:
        return {"message": "Invalid JSON format in the request body"}
    except Exception as e:
        return {"message": f"Error processing request: {e}"}


@app.post("/validate-data")
async def validate_data():
    """요청 데이터 검증 후 처리"""
    return {"message": "Valid data received"}