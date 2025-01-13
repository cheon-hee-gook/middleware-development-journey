from fastapi import FastAPI, HTTPException, Request, Depends
from starlette.middleware import Middleware
from starlette.responses import Response, JSONResponse

from app.auth import create_jwt
from app.database import users_db
# from app.middleware import (BasicRequestLoggingMiddleware, RequestBodyLoggingMiddleware, ResponseLoggingMiddleware, ProcessingTimeLoggingMiddleware)
from app.middleware import JWTAuthenticationMiddlewareBaseHTTPMiddleware, JWTAuthenticationMiddlewareStarlette, RoleAuthorizationMiddlewareBaseHTTPMiddleware, RoleAuthorizationMiddlewareStarlette
from app.schemas import LoginRequest

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
app.add_middleware(RoleAuthorizationMiddlewareStarlette, required_roles=["admin"])
# app.add_middleware(RoleAuthorizationMiddlewareBaseHTTPMiddleware, required_roles=["admin"])

# JWT 인증 미들웨어 등록
app.add_middleware(JWTAuthenticationMiddlewareStarlette, excluded_paths=["/", "/token"])
# app.add_middleware(JWTAuthenticationMiddlewareBaseHTTPMiddleware, excluded_paths=["/", "/token"])


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