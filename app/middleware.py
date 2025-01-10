from starlette.middleware.base import BaseHTTPMiddleware
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("RequestLogger")


class BasicRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request Headers: {request.headers}")
        response = await call_next(request)
        return response
