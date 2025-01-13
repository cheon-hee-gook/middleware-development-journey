from typing import Optional, Union, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import logging
import time

from app.auth import decode_jwt

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
