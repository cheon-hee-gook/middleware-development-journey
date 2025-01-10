from fastapi import FastAPI
from app.middleware import BasicRequestLoggingMiddleware

app = FastAPI()

# 요청 로깅 미들웨어 등록
app.add_middleware(BasicRequestLoggingMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello, Middleware!"}