from cryptography.fernet import Fernet
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
import logging
from dotenv import load_dotenv
import os
from redis import Redis

from app.auth import decode_jwt

# 환경 변수 로드
load_dotenv()

# 암호화 키 로드
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("Encryption key not found in .env file")

cipher_suite = Fernet(ENCRYPTION_KEY)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# 요청 로거
request_logger = logging.getLogger("RequestLogger")

# 응답 로거
response_logger = logging.getLogger("ResponseLogger")

# 처리 시간 로거
processing_logger = logging.getLogger("ProcessingLogger")


class BasicRequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청의 URL, 메서드, 헤더 정보를 로깅합니다.
    """
    async def dispatch(self, request, call_next):
        request_logger.info(f"Request URL: {request.url}")
        request_logger.info(f"Request Method: {request.method}")
        request_logger.info(f"Request Headers: {dict(request.headers)}")
        response = await call_next(request)
        return response


class RequestBodyLoggingMiddleware(BaseHTTPMiddleware):
    """
    클라이언트가 보낸 요청 본문 데이터를 로깅합니다.
    """
    async def dispatch(self, request, call_next):
        body = await request.body()
        request_logger.info(f"Request Body:{body.decode('utf-8')}")
        response = await call_next(request)
        return response


class ResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    응답 상태 코드와 데이터를 로깅합니다.
    스트리밍 응답 데이터를 처리하며 문제를 해결합니다.
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # 응답 본문 읽기
        if hasattr(response, "body"):
            body = response.body.decode("utf-8")  # JSONResponse 에서 사용
        else:
            # 스트리밍 응답 처리
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            response = Response(body, status_code=response.status_code, headers=dict(response.headers))

        response_logger.info(f"Response Status Code: {response.status_code}")
        response_logger.info(f"Response Body: {body.decode('utf-8')}")

        return response


class JWTAuthenticationMiddlewareBaseHTTPMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths=None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []

    async def dispatch(self, request, call_next):
        print(f"JWT Middleware - Request ID: {id(request)}")
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return JSONResponse({"message": "Unauthorized: No token provided"}, status_code=401)

        try:
            token = token.replace("Bearer ", "")
            payload = decode_jwt(token)
            request.state.user = payload
        except Exception as e:
            return JSONResponse({"message": f"Unauthorized: {str(e)}"}, status_code=401)

        return await call_next(request)


class JWTAuthenticationMiddlewareStarlette:
    """Starlette 기반 JWT 인증 미들웨어"""
    def __init__(self, app, excluded_paths=None):
        self.app = app
        self.excluded_paths = excluded_paths or []

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        if scope["type"] == "http" and scope["path"] not in self.excluded_paths:
            headers = dict(scope.get("headers", []))
            token = headers.get(b"authorization", b"").decode()

            if not token.startswith("Bearer "):
                response = JSONResponse({"message": "Unauthorized: No token provided"}, status_code=401)
                await response(scope, receive, send)
                return

            try:
                token = token.replace("Bearer ", "")
                payload = decode_jwt(token)
                scope.setdefault("state", {})["user"] = payload
                print(f"JWTAuthenticationMiddlewareStarlette Scope State: {scope.get('state', {})}")  # 디버깅용
            except Exception as e:
                response = JSONResponse({"message": f"Unauthorized: {str(e)}"}, status_code=401)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


class RoleAuthorizationMiddlewareBaseHTTPMiddleware(BaseHTTPMiddleware):
    """Role 기반 권한 관리 미들웨어"""
    def __init__(self, app, required_roles=None, excluded_paths=None):
        super().__init__(app)
        self.required_roles = required_roles or []
        self.excluded_paths = excluded_paths or []

    async def dispatch(self, request, call_next):
        print(f"Role Middleware - Request ID: {id(request)}")
        # 인증 제외 경로 확인
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # 사용자 정보 확인
        user = getattr(request.state, "user", None)
        if not user:
            return JSONResponse({"message": "Unauthorized: No user information"}, status_code=403)

        # 역할(Role) 확인
        user_role = user.get("role")
        if user_role not in self.required_roles:
            return JSONResponse({"message": "Forbidden: Insufficient permissions"}, status_code=403)

        return await call_next(request)


class RoleAuthorizationMiddlewareStarlette:
    """Starlette 기반 Role 권한 관리 미들웨어"""
    def __init__(self, app, required_roles=None):
        self.app = app
        self.required_roles = required_roles or []

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        # 디버깅용 로그
        print(f"Scope Type: {scope['type']}, Path: {scope['path']}")
        print(f"RoleAuthorizationMiddlewareStarlette Scope State: {scope.get('state', {})}")

        # JWT 인증을 통해 "user"가 설정되지 않았으면 권한 확인을 건너뜁니다.
        user = scope.get("state", {}).get("user")
        if not user:
            print("User not found in scope state. Skipping role authorization.")
            return await self.app(scope, receive, send)

        # 사용자 권한 확인
        user_role = user.get("role")
        print(f"Role Authorization: {user_role}")
        if user_role not in self.required_roles:
            response = JSONResponse({"message": "Forbidden: Insufficient permissions"}, status_code=403)
            await response(scope, receive, send)
            return

        # 다음 미들웨어로 이동
        await self.app(scope, receive, send)


class RequestEncryptionMiddleware(BaseHTTPMiddleware):
    """요청 데이터를 암호화하여 반환하는 미들웨어"""
    async def dispatch(self, request, call_next):
        # 요청 처리
        body = await request.body()

        try:
            # 요청 데이터를 암호화
            if body:
                encrypted_body = cipher_suite.encrypt(body)
                return Response(
                    content=encrypted_body,
                    status_code=200,
                    media_type="application/octet-stream",
                )
        except Exception as e:
            print(f"Error encrypting request: {e}")  # 디버깅
            return JSONResponse({"message": "Error encrypting request"}, status_code=500)

        return await call_next(request)


class RequestDecryptionMiddleware(BaseHTTPMiddleware):
    """요청 데이터를 복호화하여 반환하는 미들웨어"""
    async def dispatch(self, request, call_next):
        try:
            # 요청 데이터 복호화
            body = await request.body()
            if body:
                decrypted_body = cipher_suite.decrypt(body)
                return Response(
                    content=decrypted_body,
                    status_code=200,
                    media_type="application/json",
                )
        except Exception as e:
            print(f"Error decrypting request: {e}")  # 디버깅
            return JSONResponse({"message": "Error decrypting request"}, status_code=400)

        return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """요청 데이터를 검증하는 미들웨어"""

    def __init__(self, app, model):
        super().__init__(app)
        self.model = model

    async def dispatch(self, request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                self.model.parse_obj(body)  # Pydantic 모델로 데이터 검증
            except ValidationError as e:
                return JSONResponse(
                    {"message": "Invalid request data", "errors": e.errors()},
                    status_code=400,
                )
            except Exception as e:
                return JSONResponse(
                    {"message": f"Error processing request: {str(e)}"},
                    status_code=400
                )

        # 요청이 유효하면 다음 처리로 이동
        response = await call_next(request)
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """API 요청 제한 미들웨어"""

    def __init__(self, app, redis_host="localhost", redis_port=6379, rate_limit=5, window_size=60):
        super().__init__(app)
        self.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.rate_limit = rate_limit  # 허용 요청 횟수
        self.window_size = window_size  # 시간 창 (초)

    async def dispatch(self, request, call_next):
        # 클라이언트 IP 가져오기
        client_ip = request.client.host
        redis_key = f"rate_limit:{client_ip}"  # Redis 키 생성

        # 요청 횟수 가져오기
        current_count = self.redis.get(redis_key)
        if current_count is None:
            # 키가 없으면 초기화
            self.redis.set(redis_key, 1, ex=self.window_size)
        else:
            current_count = int(current_count)
            if current_count >= self.rate_limit:
                # 요청 제한 초과
                return JSONResponse(
                    {"message": "Too Many Requests. Please try again later."},
                    status_code=429
                )
            # 요청 횟수 증가
            self.redis.incr(redis_key)

        # 다음 처리
        response = await call_next(request)
        return response
