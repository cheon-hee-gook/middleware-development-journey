from starlette.middleware.base import BaseHTTPMiddleware
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("RequestLogger")


class BasicRequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청의 URL, 메서드, 헤더 정보를 로깅합니다.
    """
    async def dispatch(self, request, call_next):
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request Headers: {dict(request.headers)}")
        response = await call_next(request)
        return response


class RequestBodyLoggingMiddleware(BaseHTTPMiddleware):
    """
    클라이언트가 보낸 요청 본문 데이터를 로깅합니다.
    """
    async def dispatch(self, request, call_next):
        body = await request.body()
        logger.info(f"Request Body:{body.decode('utf-8')}")
        response = await call_next(request)
        return response
