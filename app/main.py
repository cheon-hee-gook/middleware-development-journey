from fastapi import FastAPI, HTTPException
from app.middleware import BasicRequestLoggingMiddleware, RequestBodyLoggingMiddleware

app = FastAPI()

# 요청 로깅 미들웨어 등록
app.add_middleware(BasicRequestLoggingMiddleware)

# 요청 본문 로깅 미들웨어 등록
app.add_middleware(RequestBodyLoggingMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello, Middleware!"}


@app.post("/data")
async def receive_data(payload: dict):
    if "key" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'key' in payload")
    return {"received_key": payload["key"]}