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


class ProcessingTimeLoggingMiddleware(BaseHTTPMiddleware):
    """
    각 요청의 처리 시간을 측정하여 성능 분석에 활용합니다.
    """
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        processing_time = end_time - start_time
        processing_logger.info(f"Processing Time: {processing_time:.4f} seconds")
        return response


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    요청 헤더에서 JWT를 추출하여 사용자 인증을 수행합니다.
    잘못된 입력(토큰 누락, 잘못된 토큰, 만료된 토큰)에 대해 적절한 응답을 반환합니다.
    """
    def __init__(self, app, excluded_paths: list[str] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []

    async def dispatch(self, request, call_next):
        # 제외 경로에 대해 미들웨어 동작을 생략
        for path in self.excluded_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(content={"message": "Unauthorized: No token provided"}, status_code=401)

        try:
            token = token.replace("Bearer ", "")
            payload = decode_jwt(token)
            request.state.user = payload    # 사용자 정보 저장
        except Exception as e:
            return JSONResponse(content={"message": f"Unauthorized: {e}"}, status_code=401)

        response = await call_next(request)
        return response
